from datetime import datetime
from typing import List, Dict, Any, Optional
import polars as pl
from app.data_pipeline.base import BaseDataProvider
from app.data_pipeline.yahoo_provider import yahoo_provider
from app.data_pipeline.validation import validation_service


class CryptoDataProvider(BaseDataProvider):
    """Specialized provider for 24/7 continuous cryptocurrency markets."""

    SUPPORTED_CRYPTOS = {
        "BTC": "BTC-USD",
        "BTC-USD": "BTC-USD",
        "ETH": "ETH-USD",
        "ETH-USD": "ETH-USD",
        "SOL": "SOL-USD",
        "SOL-USD": "SOL-USD",
    }

    def get_supported_timeframes(self) -> List[str]:
        return ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]

    def normalize_symbol(self, symbol: str) -> str:
        upper = symbol.upper()
        return self.SUPPORTED_CRYPTOS.get(upper, upper if "-" in upper else f"{upper}-USD")

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> pl.DataFrame:
        normalized_sym = self.normalize_symbol(symbol)
        df = await yahoo_provider.fetch_ohlcv(normalized_sym, timeframe, start_date, end_date, limit)
        
        # Crypto-specific gap detection
        gaps = validation_service.detect_missing_gaps(df, timeframe, is_crypto=True)
        if gaps:
            logger.info(f"CryptoDataProvider: Detected {len(gaps)} potential continuous gap(s) for {normalized_sym}")
            
        return df

    async def get_latest_quote(self, symbol: str) -> Dict[str, Any]:
        normalized_sym = self.normalize_symbol(symbol)
        return await yahoo_provider.get_latest_quote(normalized_sym)


crypto_provider = CryptoDataProvider()

