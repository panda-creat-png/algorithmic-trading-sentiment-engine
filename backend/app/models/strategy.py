from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.backtest import BacktestRun


class TradingStrategy(Base, TimestampMixin):
    __tablename__ = "trading_strategies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strategy_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # ma_crossover, rsi_reversal, macd, bollinger, momentum, sentiment, combined
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="strategies")
    parameter_definitions: Mapped[List["StrategyParameter"]] = relationship(
        "StrategyParameter", back_populates="strategy", cascade="all, delete-orphan"
    )
    backtest_runs: Mapped[List["BacktestRun"]] = relationship(
        "BacktestRun", back_populates="strategy", cascade="all, delete-orphan"
    )


class StrategyParameter(Base):
    __tablename__ = "strategy_parameters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("trading_strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    parameter_key: Mapped[str] = mapped_column(String(64), nullable=False)
    parameter_value: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(32), default="float", nullable=False)  # int, float, str, bool
    min_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    default_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    strategy: Mapped["TradingStrategy"] = relationship("TradingStrategy", back_populates="parameter_definitions")

