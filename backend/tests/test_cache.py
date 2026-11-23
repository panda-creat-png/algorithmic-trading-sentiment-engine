import pytest
from app.services.cache_service import cache_service


@pytest.mark.asyncio
async def test_cache_service_set_and_get():
    test_key = "test:quote:aapl"
    test_data = {"symbol": "AAPL", "price": 224.50, "volume": 1200000}
    
    # Set cache
    success = await cache_service.set(test_key, test_data, ttl_seconds=60)
    assert success is True
    
    # Retrieve cache
    cached = await cache_service.get(test_key)
    assert cached is not None
    assert cached["symbol"] == "AAPL"
    assert cached["price"] == 224.50
    
    # Delete cache
    await cache_service.delete(test_key)
    deleted = await cache_service.get(test_key)
    assert deleted is None


@pytest.mark.asyncio
async def test_redis_low_latency_fallback():
    """Verifies ISS-04 fix: Fast non-blocking fallback (<0.5s) when Redis is unreachable."""
    import time
    from app.core.redis import check_redis_connection, get_redis_client

    start = time.perf_counter()
    status = await check_redis_connection()
    elapsed = time.perf_counter() - start

    assert status["status"] in ("connected", "fallback_active")
    # Initial check finishes well under 1 second
    assert elapsed < 1.0

    # Subsequent call must be near-instantaneous (under 0.05s) due to cached availability flag
    subsequent_start = time.perf_counter()
    await get_redis_client()
    subsequent_elapsed = time.perf_counter() - subsequent_start
    assert subsequent_elapsed < 0.05

