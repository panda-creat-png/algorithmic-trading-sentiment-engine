import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_strategies_endpoint(async_client: AsyncClient):
    """Verifies that all prebuilt quantitative strategies are listed."""
    response = await async_client.get("/api/v1/strategies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    types = [s["strategy_type"] for s in data]
    assert "ma_crossover" in types
    assert "rsi_reversal" in types


@pytest.mark.asyncio
async def test_run_backtest_api_endpoint(async_client: AsyncClient):
    """Executes a real event-driven backtest simulation through the REST API."""
    payload = {
        "symbol": "NVDA",
        "strategy_type": "ma_crossover",
        "timeframe": "1d",
        "initial_capital": 100000.0,
        "fee_rate": 0.001,
        "slippage": 0.0005,
        "stop_loss_pct": 0.05,
        "take_profit_pct": 0.10,
        "parameters": {
            "fast_period": 10,
            "slow_period": 30
        }
    }
    response = await async_client.post("/api/v1/backtests/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["symbol"] == "NVDA"
    assert data["status"] == "completed"
    assert "metrics" in data
    assert "equity_curve" in data
    assert "trades" in data
    
    metrics = data["metrics"]
    assert "total_return" in metrics
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics
    assert "win_rate" in metrics

    # Also test listing backtests
    list_res = await async_client.get("/api/v1/backtests")
    assert list_res.status_code == 200
    runs = list_res.json()
    assert len(runs) >= 1
