from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple
import polars as pl
from app.core.logging import logger

TIMEFRAME_DELTAS = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
    "1wk": timedelta(weeks=1),
}


class DataValidationService:
    """High-performance Polars-based market data validation and sanity engine."""

    @staticmethod
    def normalize_to_utc(df: pl.DataFrame, timestamp_col: str = "timestamp") -> pl.DataFrame:
        """Converts timestamp column to strict UTC-aware Datetime format."""
        if df.is_empty():
            return df

        # If timestamp is string, parse to datetime
        if df[timestamp_col].dtype == pl.String:
            df = df.with_columns(
                pl.col(timestamp_col).str.to_datetime("%Y-%m-%d %H:%M:%S%z", strict=False)
            )

        # Ensure UTC timezone
        try:
            df = df.with_columns(
                pl.col(timestamp_col).dt.convert_time_zone("UTC")
            )
        except Exception:
            try:
                df = df.with_columns(
                    pl.col(timestamp_col).dt.replace_time_zone("UTC")
                )
            except Exception as e:
                logger.warning(f"Timezone conversion note: {e}")

        return df

    @staticmethod
    def validate_ohlc_integrity(df: pl.DataFrame) -> Tuple[pl.DataFrame, Dict[str, Any]]:
        """Verifies geometric price bounds: High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close."""
        if df.is_empty():
            return df, {"total_records": 0, "corrupted_records": 0, "is_valid": True}

        initial_count = len(df)

        # Logical condition for mathematically valid OHLC candle
        valid_condition = (
            (pl.col("high") >= pl.col("low")) &
            (pl.col("high") >= pl.col("open")) &
            (pl.col("high") >= pl.col("close")) &
            (pl.col("low") <= pl.col("open")) &
            (pl.col("low") <= pl.col("close")) &
            (pl.col("open") > 0) &
            (pl.col("high") > 0) &
            (pl.col("low") > 0) &
            (pl.col("close") > 0) &
            (pl.col("volume") >= 0)
        )

        valid_df = df.filter(valid_condition)
        corrupted_count = initial_count - len(valid_df)

        report = {
            "total_records": initial_count,
            "valid_records": len(valid_df),
            "corrupted_records": corrupted_count,
            "is_valid": corrupted_count == 0,
        }

        if corrupted_count > 0:
            logger.warning(f"DataValidation: Filtered {corrupted_count} corrupted OHLC candle(s).")

        return valid_df, report

    @staticmethod
    def deduplicate(df: pl.DataFrame, timestamp_col: str = "timestamp") -> pl.DataFrame:
        """Removes duplicate candles sharing the exact same timestamp, retaining the latest."""
        if df.is_empty():
            return df
        return df.unique(subset=[timestamp_col], keep="last").sort(timestamp_col)

    @staticmethod
    def compute_vwap(df: pl.DataFrame) -> pl.DataFrame:
        """Calculates Volume Weighted Average Price (VWAP) across the candle series."""
        if df.is_empty():
            return df

        # Typical price = (High + Low + Close) / 3
        typical_price = (pl.col("high") + pl.col("low") + pl.col("close")) / 3.0
        
        # Cumulative TP * Volume / Cumulative Volume
        df_with_vwap = df.with_columns([
            (typical_price * pl.col("volume")).cum_sum().alias("_cum_tp_vol"),
            pl.col("volume").cum_sum().alias("_cum_vol"),
        ]).with_columns([
            pl.when(pl.col("_cum_vol") > 0)
            .then(pl.col("_cum_tp_vol") / pl.col("_cum_vol"))
            .otherwise(pl.col("close"))
            .alias("vwap")
        ]).drop(["_cum_tp_vol", "_cum_vol"])

        return df_with_vwap

    @staticmethod
    def detect_missing_gaps(
        df: pl.DataFrame,
        timeframe: str,
        is_crypto: bool = False,
        timestamp_col: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """Identifies missing candle intervals in chronological series."""
        if len(df) < 2 or timeframe not in TIMEFRAME_DELTAS:
            return []

        expected_delta = TIMEFRAME_DELTAS[timeframe]
        timestamps = df[timestamp_col].to_list()
        gaps: List[Dict[str, Any]] = []

        for i in range(len(timestamps) - 1):
            t1 = timestamps[i]
            t2 = timestamps[i + 1]
            diff = t2 - t1

            # For crypto, market is 24/7 so any diff > 1.5 * delta is a gap
            # For stocks, we tolerate weekends (approx 2 days)
            threshold = expected_delta * 1.5
            if not is_crypto and timeframe in ("1d", "4h", "1h"):
                # If difference spans weekend (>= 2 days for 1d), allow it
                if diff > timedelta(days=3):
                    gaps.append({
                        "gap_start": t1.isoformat(),
                        "gap_end": t2.isoformat(),
                        "missing_duration_seconds": diff.total_seconds(),
                    })
            else:
                if diff > threshold:
                    gaps.append({
                        "gap_start": t1.isoformat(),
                        "gap_end": t2.isoformat(),
                        "missing_duration_seconds": diff.total_seconds(),
                    })

        return gaps


validation_service = DataValidationService()
