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


class TradeDiagnostic(BaseModel):
    trade_id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    exit_price: float
    realized_pnl: float
    pnl_pct: float
    outcome: str  # "WIN" | "LOSS" | "BREAKEVEN"
    entry_time: datetime
    exit_time: datetime
    primary_reason: str  # Main answer to 'Why This Trade Won / Why This Trade Lost'
    technical_attribution: str  # Details on RSI, Moving Averages, MACD, Bollinger Bands
    sentiment_attribution: str  # Details on FinBERT AI institutional sentiment
    risk_attribution: str  # Risk management, Stop-Loss / Take-Profit discipline
    execution_grade: str  # A+, A, B, C, F
    recommendation: str  # Key takeaway & practical rule for future trades


class PositionAnalysisRequest(BaseModel):
    symbol: str


class PositionAnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    average_entry_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    status: str  # "PROFITABLE" | "UNDERWATER" | "NEUTRAL"
    current_diagnosis: str
    technical_status: str
    sentiment_status: str
    action_advice: str  # e.g., "HOLD", "TAKE_PROFIT", "TIGHTEN_STOP_LOSS"


class PortfolioOverview(BaseModel):
    total_equity: float
    cash_balance: float
    unrealized_pnl: float
    realized_pnl: float
    total_return_pct: float
    positions: List[PositionModel]
    recent_trades: List[TradeDiagnostic] = []
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
