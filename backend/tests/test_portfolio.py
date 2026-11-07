import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_portfolio_endpoint(async_client: AsyncClient):
    """Verifies that live mark-to-market portfolio overview is returned."""
    response = await async_client.get("/api/v1/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert "total_equity" in data
    assert "cash_balance" in data
    assert "positions" in data
    assert len(data["positions"]) >= 1
    assert data["total_equity"] > 0


@pytest.mark.asyncio
async def test_paper_order_execution_and_reset(async_client: AsyncClient):
    """Verifies that BUY and SELL orders modify cash balance and positions."""
    # Reset first
    reset_res = await async_client.post("/api/v1/portfolio/reset")
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["cash_balance"] == 100000.0
    assert len(reset_data["positions"]) == 0

    # Execute BUY order of 10 shares of NVDA
    buy_payload = {"symbol": "NVDA", "side": "buy", "quantity": 10.0}
    buy_res = await async_client.post("/api/v1/portfolio/order", json=buy_payload)
    assert buy_res.status_code == 200
    buy_data = buy_res.json()
    assert buy_data["cash_balance"] < 100000.0
    assert len(buy_data["positions"]) == 1
    assert buy_data["positions"][0]["symbol"] == "NVDA"
    assert buy_data["positions"][0]["quantity"] == 10.0

    # Execute partial SELL order of 4 shares of NVDA
    sell_payload = {"symbol": "NVDA", "side": "sell", "quantity": 4.0}
    sell_res = await async_client.post("/api/v1/portfolio/order", json=sell_payload)
    assert sell_res.status_code == 200
    sell_data = sell_res.json()
    assert len(sell_data["positions"]) == 1
    assert sell_data["positions"][0]["quantity"] == 6.0

