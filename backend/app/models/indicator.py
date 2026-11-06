from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Float, String, DateTime, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.asset import Asset


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    indicator_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # SMA_20, RSI_14, MACD, etc.
    value: Mapped[float] = mapped_column(Float, nullable=False)
    secondary_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Signal line, lower band, etc.
    tertiary_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # Histogram, upper band, etc.
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="technical_indicators")

    __table_args__ = (
        UniqueConstraint("asset_id", "timeframe", "timestamp", "indicator_name", name="uq_asset_indicator_record"),
        Index("ix_indicator_query", "asset_id", "indicator_name", "timestamp"),
    )

