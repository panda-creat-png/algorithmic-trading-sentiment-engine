from typing import Optional, TYPE_CHECKING
from sqlalchemy import Float, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.news import NewsArticle
    from app.models.asset import Asset


class SentimentAnalysis(Base, TimestampMixin):
    __tablename__ = "sentiment_analysis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    
    sentiment: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # positive, negative, neutral
    positive_score: Mapped[float] = mapped_column(Float, nullable=False)
    negative_score: Mapped[float] = mapped_column(Float, nullable=False)
    neutral_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    model_name: Mapped[str] = mapped_column(String(64), default="ProsusAI/finbert", nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(32), default="1.0", nullable=True)

    # Relationships
    news_article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="sentiment_records")
    asset: Mapped[Optional["Asset"]] = relationship("Asset", back_populates="sentiments")

    __table_args__ = (
        Index("ix_sentiment_asset_created", "asset_id", "created_at"),
    )

