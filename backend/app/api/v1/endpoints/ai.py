from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.ai import (
    SentimentAnalyzeRequest,
    SentimentResult,
    SentimentBatchRequest,
    SentimentBatchResponse,
    MarketSentimentOverview,
)
from app.sentiment.finbert_engine import finbert_engine
from app.sentiment.news_ingestion import news_ingestion_service
from app.analytics.sentiment_correlation import sentiment_correlation_service
from app.services.market_data_service import market_data_service

router = APIRouter()


@router.post("/analyze", response_model=SentimentResult, summary="FinBERT Financial Sentiment Inference")
async def analyze_sentiment(payload: SentimentAnalyzeRequest):
    """Executes AI sentiment classification on input headline/snippet using FinBERT."""
    result = finbert_engine.analyze_headline(payload.text, payload.symbol)
    return SentimentResult(**result)


@router.post("/analyze/batch", response_model=SentimentBatchResponse, summary="Batch FinBERT Inference")
async def analyze_sentiment_batch(payload: SentimentBatchRequest):
    """Executes batch inference across multiple financial headlines."""
    items = [{"text": i.text, "symbol": i.symbol} for i in payload.items]
    results = finbert_engine.analyze_batch(items)
    return SentimentBatchResponse(
        total_processed=len(results),
        results=[SentimentResult(**r) for r in results]
    )


@router.get("/sentiment/{symbol}", response_model=MarketSentimentOverview, summary="Asset FinBERT Sentiment Metrics")
async def get_asset_sentiment(symbol: str, db: AsyncSession = Depends(get_db)):
    """Computes Bullish, Bearish, and Neutral indices for a specific asset based on news."""
    news = await news_ingestion_service.get_latest_news_feed(db, symbol=symbol, limit=20)
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


@router.get("/correlation/{symbol}", summary="Sentiment and Price Correlation Dynamics")
async def get_sentiment_price_correlation(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe candle window"),
    db: AsyncSession = Depends(get_db)
):
    """Investigates mathematical relationships between sentiment shifts and asset price moves."""
    from app.data_pipeline.yahoo_provider import yahoo_provider
    
    # Get candles
    candles_res = await market_data_service.get_historical_candles(db, symbol, timeframe=timeframe, limit=60)
    news = await news_ingestion_service.get_latest_news_feed(db, symbol=symbol, limit=20)

    import polars as pl
    candles_df = pl.DataFrame(candles_res.get("candles", []))
    
    analysis = sentiment_correlation_service.analyze_sentiment_price_dynamics(
        candles_df=candles_df,
        sentiments=news,
        symbol=symbol,
    )
    return analysis
