from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.news import NewsArticleResponse
from app.schemas.ai import MarketSentimentOverview

router = APIRouter()


@router.get("", response_model=List[NewsArticleResponse], summary="List Financial News")
async def list_news(
    symbol: Optional[str] = Query(None, description="Filter by ticker symbol"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Returns curated financial news articles."""
    return []


@router.get("/sentiment", response_model=MarketSentimentOverview, summary="Market-wide Sentiment Overview")
async def get_market_sentiment_overview():
    """Returns aggregated sentiment metrics across all financial news headlines."""
    return MarketSentimentOverview(
        bullish_index=0.55,
        bearish_index=0.25,
        neutral_index=0.20,
        overall_sentiment="bullish",
        sentiment_trend="improving",
        analyzed_headlines_count=0
    )


@router.get("/{symbol}", response_model=List[NewsArticleResponse], summary="Get News for Asset")
async def get_asset_news(
    symbol: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Returns news articles associated with a specific asset."""
    return []

