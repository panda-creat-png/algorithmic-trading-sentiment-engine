from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sentiment import SentimentAnalysis


class NewsArticle(Base, TimestampMixin):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(1024), unique=True, index=True, nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # Yahoo, Reddit, NewsAPI, etc.
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    author: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    raw_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    sentiment_records: Mapped[List["SentimentAnalysis"]] = relationship(
        "SentimentAnalysis", back_populates="news_article", cascade="all, delete-orphan"
    )

