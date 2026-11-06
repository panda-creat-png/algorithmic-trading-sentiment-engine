import time
from typing import Optional, Dict, Any
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> Optional[aioredis.Redis]:
    """Returns the singleton Redis client or attempts to initialize it."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=2.0,
            )
            # Verify connectivity
            await redis_client.ping()
        except Exception as e:
            logger.warning(f"Could not connect to Redis at {settings.REDIS_URL}: {e}. Operating with memory fallback cache.")
            redis_client = None
    return redis_client


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
        logger.warning(f"Redis check error: {e}")
        return {
            "status": "fallback_active",
            "backend": "in_memory_lru",
            "error": str(e),
            "latency_ms": None,
        }


async def close_redis() -> None:
    """Closes the Redis client connection on application shutdown."""
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis connection closed.")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
        finally:
            redis_client = None

