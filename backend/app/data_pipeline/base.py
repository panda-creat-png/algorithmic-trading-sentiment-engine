from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import polars as pl


class BaseDataProvider(ABC):
    """Abstract interface for financial market data providers."""

    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> pl.DataFrame:
        """Fetches OHLCV historical candle data as a standardized Polars DataFrame.
        Columns: [timestamp (Datetime UTC), open, high, low, close, volume, vwap]
        """
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """Returns list of timeframes supported by provider (e.g. ['1m', '5m', '15m', '1h', '4h', '1d', '1wk'])."""
        pass

    @abstractmethod
    async def get_latest_quote(self, symbol: str) -> Dict[str, Any]:
        """Returns real-time or latest available quote dictionary."""
        pass

