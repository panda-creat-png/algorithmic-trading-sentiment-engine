from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class BacktestRequest(BaseModel):
    strategy_id: int
    symbol: str = Field(..., max_length=32)
    start_date: datetime
    end_date: datetime
    timeframe: str = Field(default="1d", max_length=16)
    initial_capital: float = Field(default=100000.0, gt=0)
    fee_rate: float = Field(default=0.001, ge=0)       # 0.1% per trade
    slippage: float = Field(default=0.0005, ge=0)     # 5 bps
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    size: float
    fee: float
    slippage: float
    realized_pnl: float
    pnl_percentage: float
    exit_reason: str

    model_config = ConfigDict(from_attributes=True)


class BacktestMetrics(BaseModel):
    total_return: Optional[float] = None
    cagr: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    calmar_ratio: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    total_trades: int = 0
    annualized_volatility: Optional[float] = None
    exposure_time: Optional[float] = None
    benchmark_return: Optional[float] = None  # Buy & hold comparison


class BacktestResponse(BaseModel):
    id: int
    strategy_id: int
    asset_id: int
    symbol: Optional[str] = None
    status: str
    start_date: datetime
    end_date: datetime
    timeframe: str
    initial_capital: float
    final_equity: Optional[float] = None
    metrics: BacktestMetrics
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

