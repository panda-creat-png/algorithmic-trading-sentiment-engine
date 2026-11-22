from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.asset import Asset


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    
    total_equity: Mapped[float] = mapped_column(Float, nullable=False)
    cash_balance: Mapped[float] = mapped_column(Float, nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    positions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="portfolio_snapshots")


class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="watchlists")
    items: Mapped[List["WatchlistItem"]] = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="watchlist_items")


class PaperAccount(Base, TimestampMixin):
    """Persistent storage for paper trading balance and realized P&L."""
    __tablename__ = "paper_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[str] = mapped_column(String(64), unique=True, default="default", index=True, nullable=False)
    cash_balance: Mapped[float] = mapped_column(Float, default=100000.0, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class PaperPosition(Base, TimestampMixin):
    """Persistent storage for active paper portfolio positions."""
    __tablename__ = "paper_positions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[str] = mapped_column(String(64), default="default", index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    average_entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class PaperTrade(Base, TimestampMixin):
    """Persistent trade journal and AI Trade Diagnostics & Autopsy history."""
    __tablename__ = "paper_trades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trade_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    account_id: Mapped[str] = mapped_column(String(64), default="default", index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float] = mapped_column(Float, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pnl_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    exit_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    primary_reason: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    technical_attribution: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    sentiment_attribution: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    risk_attribution: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    execution_grade: Mapped[str] = mapped_column(String(16), default="B", nullable=False)
    recommendation: Mapped[str] = mapped_column(String(1000), default="", nullable=False)

