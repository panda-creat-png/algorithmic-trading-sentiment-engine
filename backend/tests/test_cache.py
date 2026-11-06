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

