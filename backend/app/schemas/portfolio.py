from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class PositionModel(BaseModel):
    symbol: str
    quantity: float
    average_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float


class PortfolioOverview(BaseModel):
    total_equity: float
    cash_balance: float
    unrealized_pnl: float
    realized_pnl: float
    total_return_pct: float
    positions: List[PositionModel]
    timestamp: datetime


class PaperOrderRequest(BaseModel):
    symbol: str = Field(..., max_length=32)
    side: str = Field(..., description="buy | sell")
    quantity: float = Field(..., gt=0)


class SimulationRequest(BaseModel):
    initial_cash: float = Field(default=100000.0, gt=0)
    allocations: Dict[str, float] = Field(..., description="Map of symbol -> fraction or amount (sum <= 1.0)")
    rebalance_frequency: str = Field(default="1m", description="1w, 1m, 1q")
    start_date: datetime
    end_date: datetime
