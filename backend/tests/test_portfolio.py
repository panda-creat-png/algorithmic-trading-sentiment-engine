import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_portfolio_endpoint(async_client: AsyncClient):
    """Verifies that live mark-to-market portfolio overview is returned with trade diagnostics."""
    response = await async_client.get("/api/v1/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert "total_equity" in data
    assert "cash_balance" in data
    assert "positions" in data
    assert "recent_trades" in data
    assert len(data["positions"]) >= 1
    assert data["total_equity"] > 0


@pytest.mark.asyncio
async def test_get_trade_diagnostics_endpoint(async_client: AsyncClient):
    """Verifies retrieval of full AI trade autopsy and attribution journal."""
    response = await async_client.get("/api/v1/portfolio/trades")
    assert response.status_code == 200
    trades = response.json()
    assert isinstance(trades, list)
    assert len(trades) >= 1
    sample = trades[0]
    assert "trade_id" in sample
    assert "symbol" in sample
    assert "outcome" in sample
    assert sample["outcome"] in ("WIN", "LOSS", "BREAKEVEN")
    assert "primary_reason" in sample
    assert "technical_attribution" in sample
    assert "sentiment_attribution" in sample
    assert "risk_attribution" in sample
    assert "execution_grade" in sample
    assert "recommendation" in sample


@pytest.mark.asyncio
async def test_analyze_active_position_endpoint(async_client: AsyncClient):
    """Verifies real-time AI diagnosis on an open position."""
    # First ensure NVDA position exists
    buy_payload = {"symbol": "NVDA", "side": "buy", "quantity": 5.0}
    await async_client.post("/api/v1/portfolio/order", json=buy_payload)

    response = await async_client.post("/api/v1/portfolio/analyze-position", json={"symbol": "NVDA"})
    assert response.status_code == 200
    diag = response.json()
    assert diag["symbol"] == "NVDA"
    assert "status" in diag
    assert "current_diagnosis" in diag
    assert "technical_status" in diag
    assert "sentiment_status" in diag
    assert "action_advice" in diag


@pytest.mark.asyncio
async def test_paper_order_execution_and_reset(async_client: AsyncClient):
    """Verifies that BUY and SELL orders modify cash balance, positions, and generate trade diagnostics."""
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
    # Check that trade diagnostic was generated
    assert len(sell_data["recent_trades"]) >= 1
    latest_trade = sell_data["recent_trades"][0]
    assert latest_trade["symbol"] == "NVDA"
    assert latest_trade["quantity"] == 4.0
    assert "primary_reason" in latest_trade


@pytest.mark.asyncio
async def test_portfolio_database_persistence_across_service_instances(async_client: AsyncClient, db_session):
    """Verifies ISS-02 fix: Paper trading positions and account state survive service re-instantiation / restarts."""
    from app.services.portfolio_service import PaperPortfolioService

    # 1. Reset and buy AAPL shares
    await async_client.post("/api/v1/portfolio/reset")
    buy_res = await async_client.post("/api/v1/portfolio/order", json={"symbol": "AAPL", "side": "buy", "quantity": 15.0})
    assert buy_res.status_code == 200
    buy_data = buy_res.json()
    expected_cash = buy_data["cash_balance"]

    # 2. Re-instantiate PaperPortfolioService from scratch (simulating backend reboot)
    rebooted_service = PaperPortfolioService()
    rebooted_overview = await rebooted_service.get_overview(db=db_session)

    # 3. Assert that state was faithfully restored from database
    assert rebooted_overview.cash_balance == expected_cash
    assert len(rebooted_overview.positions) == 1
    assert rebooted_overview.positions[0].symbol == "AAPL"
    assert rebooted_overview.positions[0].quantity == 15.0
