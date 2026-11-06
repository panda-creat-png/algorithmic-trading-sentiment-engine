from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.market_data import MarketData
    from app.models.indicator import TechnicalIndicator
    from app.models.sentiment import SentimentAnalysis
    from app.models.backtest import BacktestRun
    from app.models.portfolio import WatchlistItem


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(32), default="stock", index=True, nullable=False)  # stock, crypto, forex
    exchange: Mapped[str] = mapped_column(String(64), default="US", nullable=False)
    currency: Mapped[str] = mapped_column(String(16), default="USD", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    candles: Mapped[List["MarketData"]] = relationship("MarketData", back_populates="asset", cascade="all, delete-orphan")
    technical_indicators: Mapped[List["TechnicalIndicator"]] = relationship("TechnicalIndicator", back_populates="asset", cascade="all, delete-orphan")
    sentiments: Mapped[List["SentimentAnalysis"]] = relationship("SentimentAnalysis", back_populates="asset", cascade="all, delete-orphan")
    backtest_runs: Mapped[List["BacktestRun"]] = relationship("BacktestRun", back_populates="asset")
    watchlist_items: Mapped[List["WatchlistItem"]] = relationship("WatchlistItem", back_populates="asset", cascade="all, delete-orphan")

