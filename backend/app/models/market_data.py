from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.asset import Asset


class MarketData(Base):
    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # 1m, 5m, 15m, 1h, 4h, 1d, 1wk
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    trades_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vwap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="candles")

    __table_args__ = (
        UniqueConstraint("asset_id", "timeframe", "timestamp", name="uq_asset_timeframe_timestamp"),
        Index("ix_market_data_asset_timeframe_timestamp", "asset_id", "timeframe", "timestamp"),
    )

