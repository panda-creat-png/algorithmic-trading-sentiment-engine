from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.portfolio import PortfolioOverview, PositionModel, SimulationRequest

router = APIRouter()


@router.get("", response_model=PortfolioOverview, summary="Get Current Paper Portfolio")
async def get_portfolio():
    """Returns paper portfolio equity, cash, unrealized/realized PnL, and current positions."""
    return PortfolioOverview(
        total_equity=125430.50,
        cash_balance=45200.00,
        unrealized_pnl=4230.50,
        realized_pnl=21200.00,
        total_return_pct=25.43,
        positions=[
            PositionModel(
                symbol="NVDA",
                quantity=40,
                average_entry_price=112.50,
                current_price=138.20,
                market_value=5528.00,
                unrealized_pnl=1028.00,
                unrealized_pnl_pct=22.84,
            ),
            PositionModel(
                symbol="AAPL",
                quantity=150,
                average_entry_price=215.00,
                current_price=227.40,
                market_value=34110.00,
                unrealized_pnl=1860.00,
                unrealized_pnl_pct=5.77,
            ),
            PositionModel(
                symbol="BTC-USD",
                quantity=0.65,
                average_entry_price=62400.00,
                current_price=66250.00,
                market_value=43062.50,
                unrealized_pnl=2502.50,
                unrealized_pnl_pct=6.17,
            ),
        ],
        timestamp=datetime.now(timezone.utc)
    )


@router.post("/simulate", summary="Run Portfolio Rebalancing Simulation")
async def simulate_portfolio(payload: SimulationRequest):
    """Simulates multi-asset portfolio weights and historical rebalancing returns."""
    return {
        "status": "simulated",
        "initial_cash": payload.initial_cash,
        "final_value": payload.initial_cash * 1.22,
        "cagr": 0.198,
        "max_drawdown": -0.114,
        "sharpe_ratio": 1.54,
        "rebalance_count": 12,
    }

