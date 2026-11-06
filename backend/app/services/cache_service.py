import json
import time
from typing import Any, Optional
from app.core.redis import get_redis_client
from app.core.logging import logger


class MemoryCache:
    """Thread-safe fast in-memory TTL cache fallback for development/offline mode."""
    def __init__(self):
        self._store: dict[str, tuple[Any, Optional[float]]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if expiry is not None and time.time() > expiry:
            del self._store[key]
            return None
        return val

    def set(self, key: str, val: Any, ttl: Optional[int] = None) -> None:
        expiry = (time.time() + ttl) if ttl is not None else None
        self._store[key] = (val, expiry)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


_memory_cache = MemoryCache()


class CacheService:
    """Unified caching service utilizing Redis with transparent memory cache fallback."""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        try:
            client = await get_redis_client()
            if client:
                data = await client.get(key)
                if data:
                    return json.loads(data)
                return None
        except Exception as e:
            logger.debug(f"Redis get error for {key}: {e}. Falling back to memory cache.")
        
        # Fallback
        cached_str = _memory_cache.get(key)
        if cached_str is not None:
            return json.loads(cached_str) if isinstance(cached_str, str) else cached_str
        return None

    @staticmethod
    async def set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
        serialized = json.dumps(value, default=str)
        try:
            client = await get_redis_client()
            if client:
                await client.set(key, serialized, ex=ttl_seconds)
                return True
        except Exception as e:
            logger.debug(f"Redis set error for {key}: {e}. Falling back to memory cache.")
        
        # Fallback
        _memory_cache.set(key, serialized, ttl=ttl_seconds)
        return True

    @staticmethod
    async def delete(key: str) -> bool:
        try:
            client = await get_redis_client()
            if client:
                await client.delete(key)
        except Exception as e:
            logger.debug(f"Redis delete error for {key}: {e}")
        
        _memory_cache.delete(key)
        return True


cache_service = CacheService()

