import json
from typing import Optional, List, Dict, Any
from app.services.cache_service import cache_service
from app.core.logging import logger

CACHE_TTLS = {
    "1m": 30,       # 30 seconds
    "5m": 120,      # 2 minutes
    "15m": 300,     # 5 minutes
    "1h": 900,      # 15 minutes
    "4h": 1800,     # 30 minutes
    "1d": 3600,     # 1 hour
    "1wk": 7200,    # 2 hours
}


class DataCacheService:
    """Specialized market data caching service with timeframe-aware TTL."""

    @staticmethod
    def _make_key(symbol: str, timeframe: str, limit: int) -> str:
        return f"market:ohlcv:{symbol.upper()}:{timeframe}:{limit}"

    @staticmethod
    def _make_quote_key(symbol: str) -> str:
        return f"market:quote:{symbol.upper()}"

    @classmethod
    async def get_candles(cls, symbol: str, timeframe: str, limit: int) -> Optional[List[Dict[str, Any]]]:
        key = cls._make_key(symbol, timeframe, limit)
        return await cache_service.get(key)

    @classmethod
    async def set_candles(cls, symbol: str, timeframe: str, limit: int, candles: List[Dict[str, Any]]) -> None:
        key = cls._make_key(symbol, timeframe, limit)
        ttl = CACHE_TTLS.get(timeframe, 300)
        await cache_service.set(key, candles, ttl_seconds=ttl)

    @classmethod
    async def get_quote(cls, symbol: str) -> Optional[Dict[str, Any]]:
        key = cls._make_quote_key(symbol)
        return await cache_service.get(key)

    @classmethod
    async def set_quote(cls, symbol: str, quote: Dict[str, Any]) -> None:
        key = cls._make_quote_key(symbol)
        # Quote TTL: 15 seconds
        await cache_service.set(key, quote, ttl_seconds=15)


data_cache_service = DataCacheService()
