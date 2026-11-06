from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.news import NewsArticleResponse
from app.schemas.ai import MarketSentimentOverview
from app.sentiment.news_ingestion import news_ingestion_service
from app.sentiment.finbert_engine import finbert_engine

router = APIRouter()


@router.get("", summary="List Curated Financial News with Sentiment")
async def list_news(
    symbol: Optional[str] = Query(None, description="Filter by ticker symbol"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Returns curated financial news articles with real FinBERT sentiment scores."""
    return await news_ingestion_service.get_latest_news_feed(db, symbol=symbol, limit=limit)


@router.get("/sentiment", response_model=MarketSentimentOverview, summary="Market-wide Sentiment Overview")
async def get_market_sentiment_overview(db: AsyncSession = Depends(get_db)):
    """Returns aggregated sentiment metrics across all financial news headlines."""
    news = await news_ingestion_service.get_latest_news_feed(db, limit=30)
    sentiment_records = [
        {
            "positive_score": n.get("positive_score", 0.5),
            "negative_score": n.get("negative_score", 0.2),
            "neutral_score": n.get("neutral_score", 0.3),
        }
        for n in news
    ]
    aggregated = finbert_engine.aggregate_sentiment_metrics(sentiment_records)
    return MarketSentimentOverview(**aggregated)


@router.post("/sync", summary="Trigger Financial News Ingestion")
async def sync_financial_news(
    background_tasks: BackgroundTasks,
    symbols: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Triggers background scraping and FinBERT analysis of financial news."""
    async def _run_sync(syms: Optional[List[str]]):
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await news_ingestion_service.fetch_and_ingest_news(session, symbols=syms)

    background_tasks.add_task(_run_sync, symbols)
    return {"status": "news_sync_scheduled", "symbols": symbols or ["NVDA", "AAPL", "MSFT", "BTC-USD"]}


@router.get("/{symbol}", summary="Get News for Asset")
async def get_asset_news(
    symbol: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Returns news articles associated with a specific asset."""
    return await news_ingestion_service.get_latest_news_feed(db, symbol=symbol, limit=limit)
