from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AssetBase(BaseModel):
    symbol: str = Field(..., max_length=32)
    name: str = Field(..., max_length=255)
    asset_class: str = Field(default="stock", max_length=32)
    exchange: str = Field(default="US", max_length=64)
    currency: str = Field(default="USD", max_length=16)
    is_active: bool = True


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandleResponse(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades_count: Optional[int] = None
    vwap: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class MarketHistoryResponse(BaseModel):
    symbol: str
    timeframe: str
    total_candles: int
    candles: List[CandleResponse]


class IndicatorDataPoint(BaseModel):
    timestamp: datetime
    value: float
    secondary_value: Optional[float] = None
    tertiary_value: Optional[float] = None


class IndicatorResponse(BaseModel):
    symbol: str
    indicator_name: str
    timeframe: str
    data: List[IndicatorDataPoint]

