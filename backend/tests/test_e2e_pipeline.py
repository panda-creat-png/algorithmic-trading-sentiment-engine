import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_end_to_end_research_pipeline(async_client: AsyncClient):
    """
    Complete End-to-End QuantMind AI Research & Simulation Pipeline:
    1. Register & Authenticate User (JWT).
    2. Ingest Market Data & Verify Polars Technical Indicators.
    3. Run AI FinBERT Sentiment Inference on Financial News.
    4. Execute Event-Driven Strategy Backtest.
    5. Route Mark-to-Market Paper Order.
    """
    # -------------------------------------------------------------
    # STEP 1: Register User & Obtain JWT Access Token
    # -------------------------------------------------------------
    email = "e2e_quant@quantmind.ai"
    password = "QuantMindE2ESecurePassword!"
    reg_res = await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "E2E Lead Quantitative Engineer"
    })
    assert reg_res.status_code == 201
    auth_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Verify user profile
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # -------------------------------------------------------------
    # STEP 2: Ingest Market History & Technical Indicators
    # -------------------------------------------------------------
    ind_res = await async_client.get("/api/v1/market/NVDA/indicators?timeframe=1d&limit=40")
    assert ind_res.status_code == 200
    ind_data = ind_res.json()
    assert ind_data["symbol"] == "NVDA"
    assert "latest_metrics" in ind_data
    assert "signals" in ind_data
    assert ind_data["bias"] in ("BULLISH", "BEARISH", "NEUTRAL")

    # -------------------------------------------------------------
    # STEP 3: Run AI FinBERT Financial Sentiment Inference
    # -------------------------------------------------------------
    ai_res = await async_client.post("/api/v1/ai/analyze", json={
        "text": "NVIDIA reports historic datacenter revenue exceeding Wall Street forecasts",
        "symbol": "NVDA"
    })
    assert ai_res.status_code == 200
    sentiment_data = ai_res.json()
    assert sentiment_data["sentiment"] in ("positive", "negative", "neutral")
    assert "positive_score" in sentiment_data
    assert "confidence" in sentiment_data

    # -------------------------------------------------------------
    # STEP 4: Run Event-Driven Strategy Backtest
    # -------------------------------------------------------------
    backtest_payload = {
        "symbol": "NVDA",
        "strategy_type": "ma_crossover",
        "timeframe": "1d",
        "initial_capital": 100000.0,
        "fee_rate": 0.001,
        "slippage": 0.0005,
        "parameters": {
            "fast_period": 10,
            "slow_period": 25
        }
    }
    bt_res = await async_client.post("/api/v1/backtests/run", json=backtest_payload, headers=headers)
    assert bt_res.status_code == 200
    bt_data = bt_res.json()
    assert bt_data["status"] == "completed"
    assert "metrics" in bt_data
    assert "equity_curve" in bt_data
    assert "trades" in bt_data

    # -------------------------------------------------------------
    # STEP 5: Route Mark-to-Market Paper Order
    # -------------------------------------------------------------
    order_payload = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 15.0
    }
    order_res = await async_client.post("/api/v1/portfolio/order", json=order_payload, headers=headers)
    assert order_res.status_code == 200
    portfolio_data = order_res.json()
    assert portfolio_data["total_equity"] > 0
    symbols_in_portfolio = [p["symbol"] for p in portfolio_data["positions"]]
    assert "NVDA" in symbols_in_portfolio

