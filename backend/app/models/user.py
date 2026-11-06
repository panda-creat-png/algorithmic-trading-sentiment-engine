from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.strategy import TradingStrategy
    from app.models.portfolio import PortfolioSnapshot, Watchlist


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    strategies: Mapped[List["TradingStrategy"]] = relationship("TradingStrategy", back_populates="user", cascade="all, delete-orphan")
    portfolio_snapshots: Mapped[List["PortfolioSnapshot"]] = relationship("PortfolioSnapshot", back_populates="user", cascade="all, delete-orphan")
    watchlists: Mapped[List["Watchlist"]] = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")

