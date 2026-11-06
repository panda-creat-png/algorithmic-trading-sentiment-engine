import pytest
from httpx import AsyncClient
from app.data_pipeline.yahoo_provider import yahoo_provider
from app.data_pipeline.crypto_provider import crypto_provider


@pytest.mark.asyncio
async def test_yahoo_provider_fetch_ohlcv():
    # Test fetching 5 days of AAPL daily candles
    df = await yahoo_provider.fetch_ohlcv("AAPL", timeframe="1d", limit=5)
    assert not df.is_empty()
    assert len(df) <= 5
    assert "timestamp" in df.columns
    assert "open" in df.columns
    assert "high" in df.columns
    assert "low" in df.columns
    assert "close" in df.columns
    assert "volume" in df.columns
    assert "vwap" in df.columns
    # Check price validity
    assert df["close"][0] > 0
    assert df["high"][0] >= df["low"][0]


@pytest.mark.asyncio
async def test_crypto_provider_normalization():
    norm = crypto_provider.normalize_symbol("BTC")
    assert norm == "BTC-USD"
    norm_eth = crypto_provider.normalize_symbol("ETH")
    assert norm_eth == "ETH-USD"


@pytest.mark.asyncio
async def test_market_history_api_endpoint(async_client: AsyncClient):
    # Call historical candles endpoint for AAPL
    response = await async_client.get("/api/v1/market/AAPL/history?timeframe=1d&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["timeframe"] == "1d"
    assert "candles" in data
    assert len(data["candles"]) > 0
    first_candle = data["candles"][0]
    assert "open" in first_candle
    assert "close" in first_candle
    assert "timestamp" in first_candle


@pytest.mark.asyncio
async def test_market_quote_api_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/market/AAPL/quote")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] > 0
    assert "change" in data
    assert "change_percent" in data
    assert "day_high" in data
    assert "day_low" in data

