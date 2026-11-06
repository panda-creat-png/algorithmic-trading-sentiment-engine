from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class StrategyBase(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = None
    strategy_type: str = Field(..., description="ma_crossover | rsi_reversal | macd | bollinger | momentum | sentiment | combined")
    is_active: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    strategy_type: Optional[str] = None
    is_active: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None


class StrategyResponse(StrategyBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

