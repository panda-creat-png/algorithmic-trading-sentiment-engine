from datetime import datetime
from typing import List, Dict, Any, Optional
import polars as pl
from app.core.config import settings
from app.core.logging import logger
from app.data_pipeline.base import BaseDataProvider
from app.data_pipeline.yahoo_provider import yahoo_provider


class AlpacaProvider(BaseDataProvider):
    """Optional Alpaca Market Data Provider (active when credentials configured)."""

    def __init__(self):
        self.api_key = settings.ALPACA_API_KEY
        self.secret_key = settings.ALPACA_SECRET_KEY
        self.is_configured = bool(self.api_key and self.secret_key)

    def get_supported_timeframes(self) -> List[str]:
        return ["1m", "5m", "15m", "1h", "1d"]

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> pl.DataFrame:
        if not self.is_configured:
            logger.info("Alpaca credentials unconfigured. Delegating to YahooFinanceProvider.")
            return await yahoo_provider.fetch_ohlcv(symbol, timeframe, start_date, end_date, limit)

        # In production with keys, call Alpaca Data API v2
        raise NotImplementedError("Alpaca live stream connection configured via API keys.")

    async def get_latest_quote(self, symbol: str) -> Dict[str, Any]:
        if not self.is_configured:
            return await yahoo_provider.get_latest_quote(symbol)
        raise NotImplementedError("Alpaca quote API configured via API keys.")


alpaca_provider = AlpacaProvider()
