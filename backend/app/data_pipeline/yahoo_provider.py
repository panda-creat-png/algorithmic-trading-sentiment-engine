import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd
import polars as pl
from app.data_pipeline.base import BaseDataProvider
from app.data_pipeline.validation import validation_service
from app.core.logging import logger

TIMEFRAME_MAP = {
    "1m": {"interval": "1m", "default_period": "5d"},
    "5m": {"interval": "5m", "default_period": "1mo"},
    "15m": {"interval": "15m", "default_period": "1mo"},
    "1h": {"interval": "1h", "default_period": "6mo"},
    "4h": {"interval": "1h", "default_period": "1y", "resample": "4h"},
    "1d": {"interval": "1d", "default_period": "2y"},
    "1wk": {"interval": "1wk", "default_period": "5y"},
}


class YahooFinanceProvider(BaseDataProvider):
    """Production provider integrating Yahoo Finance for equities and crypto."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_supported_timeframes(self) -> List[str]:
        return list(TIMEFRAME_MAP.keys())

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> pl.DataFrame:
        """Fetches OHLCV historical market candles and returns a validated Polars DataFrame."""
        if timeframe not in TIMEFRAME_MAP:
            raise ValueError(f"Unsupported timeframe: {timeframe}. Supported: {self.get_supported_timeframes()}")

        cfg = TIMEFRAME_MAP[timeframe]
        interval = cfg["interval"]
        period = cfg.get("default_period", "1y")

        # Execute yfinance blocking I/O in thread pool to prevent blocking asyncio loop
        loop = asyncio.get_running_loop()
        df_pandas = await loop.run_in_executor(
            None,
            lambda: self._fetch_yfinance_history(symbol, interval, period, start_date, end_date)
        )

        if df_pandas is None or df_pandas.empty:
            logger.warning(f"YahooFinanceProvider: Empty data returned for {symbol} ({timeframe})")
            return pl.DataFrame(schema={
                "timestamp": pl.Datetime(time_unit="us", time_zone="UTC"),
                "open": pl.Float64,
                "high": pl.Float64,
                "low": pl.Float64,
                "close": pl.Float64,
                "volume": pl.Float64,
                "vwap": pl.Float64,
            })

        # Reset index to extract Date/Datetime column
        df_pandas = df_pandas.reset_index()
        date_col = "Datetime" if "Datetime" in df_pandas.columns else "Date"

        # Convert timestamps to list of Python UTC datetimes (avoids numpy datetime64 resolution mismatches)
        timestamps = [pd.to_datetime(t, utc=True).to_pydatetime() for t in df_pandas[date_col]]

        # Build Polars DataFrame
        pl_dict = {
            "timestamp": timestamps,
            "open": [float(x) for x in df_pandas["Open"]],
            "high": [float(x) for x in df_pandas["High"]],
            "low": [float(x) for x in df_pandas["Low"]],
            "close": [float(x) for x in df_pandas["Close"]],
            "volume": [float(x) for x in df_pandas["Volume"]],
        }

        df = pl.DataFrame(pl_dict)

        # Normalize UTC timezone
        df = validation_service.normalize_to_utc(df, "timestamp")

        # Resample if needed (e.g. 4h resampled from 1h)
        if cfg.get("resample") == "4h" and len(df) > 0:
            df = df.group_by_dynamic("timestamp", every="4h").agg([
                pl.col("open").first().alias("open"),
                pl.col("high").max().alias("high"),
                pl.col("low").min().alias("low"),
                pl.col("close").last().alias("close"),
                pl.col("volume").sum().alias("volume"),
            ])

        # Deduplicate
        df = validation_service.deduplicate(df, "timestamp")

        # Validate OHLC geometric integrity
        df, report = validation_service.validate_ohlc_integrity(df)

        # Compute VWAP
        df = validation_service.compute_vwap(df)

        # Apply limit to latest candles
        if limit and len(df) > limit:
            df = df.tail(limit)

        return df

    def _fetch_yfinance_history(
        self,
        symbol: str,
        interval: str,
        period: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ):
        """Internal synchronous helper with retry logic for yfinance."""
        for attempt in range(1, self.max_retries + 1):
            try:
                ticker = yf.Ticker(symbol)
                if start_date and end_date:
                    df = ticker.history(start=start_date, end=end_date, interval=interval, auto_adjust=False)
                else:
                    df = ticker.history(period=period, interval=interval, auto_adjust=False)
                return df
            except Exception as e:
                logger.warning(f"YahooFinance fetch attempt {attempt}/{self.max_retries} failed for {symbol}: {e}")
                if attempt == self.max_retries:
                    raise
                import time
                time.sleep(self.retry_delay * attempt)
        return None

    async def get_latest_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetches real-time price, day high/low, and 24h metrics."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self._get_quote_sync(symbol))

    def _get_quote_sync(self, symbol: str) -> Dict[str, Any]:
        ticker = yf.Ticker(symbol)
        try:
            fast_info = getattr(ticker, "fast_info", None)
            if fast_info:
                last_price = float(fast_info.last_price or 0.0)
                prev_close = float(fast_info.previous_close or last_price)
                change = round(last_price - prev_close, 2)
                change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0
                return {
                    "symbol": symbol.upper(),
                    "price": last_price,
                    "previous_close": prev_close,
                    "change": change,
                    "change_percent": change_pct,
                    "day_high": float(fast_info.day_high or last_price),
                    "day_low": float(fast_info.day_low or last_price),
                    "volume": float(fast_info.last_volume or 0.0),
                    "year_high": float(fast_info.year_high or 0.0),
                    "year_low": float(fast_info.year_low or 0.0),
                    "currency": getattr(fast_info, "currency", "USD"),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            logger.debug(f"Fast info error for {symbol}: {e}. Falling back to 1d history.")

        # Fallback to history
        df = ticker.history(period="2d", interval="1d")
        if not df.empty:
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else last_row
            last_price = float(last_row["Close"])
            prev_close = float(prev_row["Close"])
            change = round(last_price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0
            return {
                "symbol": symbol.upper(),
                "price": last_price,
                "previous_close": prev_close,
                "change": change,
                "change_percent": change_pct,
                "day_high": float(last_row["High"]),
                "day_low": float(last_row["Low"]),
                "volume": float(last_row["Volume"]),
                "currency": "USD",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        raise RuntimeError(f"Unable to retrieve market quote for {symbol}")


yahoo_provider = YahooFinanceProvider()
