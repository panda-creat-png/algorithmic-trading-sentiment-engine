import time
import asyncio
from typing import Optional, Dict, Any
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

redis_client: Optional[aioredis.Redis] = None
_redis_available: Optional[bool] = None
_last_check_time: float = 0.0
_RECONNECT_COOLDOWN_SECONDS: float = 30.0  # Avoid trying TCP connection on every call when offline
_CONNECT_TIMEOUT_SECONDS: float = 0.3      # Quick non-blocking timeout for initial connectivity check


async def get_redis_client() -> Optional[aioredis.Redis]:
    """
    Returns the singleton Redis client or attempts to initialize it with low-latency timeout.
    If Redis is unreachable, flags unavailability and immediately returns None to use memory cache.
    """
    global redis_client, _redis_available, _last_check_time

    # If Redis is active and connected, return client immediately
    if redis_client is not None and _redis_available is True:
        return redis_client

    now = time.time()
    # If previously marked unavailable, skip trying to reconnect until cooldown expires
    if _redis_available is False and (now - _last_check_time) < _RECONNECT_COOLDOWN_SECONDS:
        return None

    _last_check_time = now
    try:
        temp_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=_CONNECT_TIMEOUT_SECONDS,
            socket_timeout=_CONNECT_TIMEOUT_SECONDS,
        )
        # Fast connectivity ping
        await asyncio.wait_for(temp_client.ping(), timeout=_CONNECT_TIMEOUT_SECONDS)
        redis_client = temp_client
        _redis_available = True
        logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        return redis_client
    except Exception as e:
        if _redis_available is not False:
            logger.warning(
                f"Redis unavailable at {settings.REDIS_URL} ({e}). Fast memory fallback active (re-check every {_RECONNECT_COOLDOWN_SECONDS}s)."
            )
        _redis_available = False
        redis_client = None
        return None


def mark_redis_error():
    """Marks Redis as temporarily down if a command fails during runtime."""
    global redis_client, _redis_available, _last_check_time
    _redis_available = False
    _last_check_time = time.time()
    redis_client = None


async def check_redis_connection() -> Dict[str, Any]:
    """Tests the Redis connection and returns latency and status."""
    start_time = time.perf_counter()
    try:
        client = await get_redis_client()
        if client:
            await client.ping()
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "connected",
                "backend": "redis",
                "latency_ms": latency_ms,
            }
        else:
            return {
                "status": "fallback_active",
                "backend": "in_memory_lru",
                "note": "Redis offline; using fast memory cache",
                "latency_ms": 0.05,
            }
    except Exception as e:
        mark_redis_error()
        logger.warning(f"Redis check error: {e}")
        return {
            "status": "fallback_active",
            "backend": "in_memory_lru",
            "error": str(e),
            "latency_ms": None,
        }


async def close_redis() -> None:
    """Closes the Redis client connection on application shutdown."""
    global redis_client, _redis_available
    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis connection closed.")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
        finally:
            redis_client = None
            _redis_available = None

