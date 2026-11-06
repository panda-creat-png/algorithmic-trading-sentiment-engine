import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset
from app.models.market_data import MarketData
from app.models.strategy import TradingStrategy
from app.models.news import NewsArticle
from app.models.sentiment import SentimentAnalysis


@pytest.mark.asyncio
async def test_asset_and_candle_creation(db_session: AsyncSession):
    # Create Asset
    asset = Asset(
        symbol="NVDA",
        name="NVIDIA Corporation",
        asset_class="stock",
        exchange="NASDAQ",
        currency="USD"
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    assert asset.id is not None
    assert asset.symbol == "NVDA"

    # Create MarketData candle
    candle = MarketData(
        asset_id=asset.id,
        timeframe="1d",
        timestamp=datetime.now(timezone.utc),
        open=120.50,
        high=125.00,
        low=119.80,
        close=124.30,
        volume=45000000.0,
        vwap=123.10
    )
    db_session.add(candle)
    await db_session.commit()
    await db_session.refresh(candle)
    assert candle.id is not None
    assert candle.asset_id == asset.id
    assert candle.close == 124.30


@pytest.mark.asyncio
async def test_news_and_sentiment_relation(db_session: AsyncSession):
    news = NewsArticle(
        title="NVIDIA announces next-generation AI architecture",
        url="https://example.com/news/nvda-ai-1",
        source="Bloomberg",
        summary="Record performance in benchmark tests",
        published_at=datetime.now(timezone.utc)
    )
    db_session.add(news)
    await db_session.commit()
    await db_session.refresh(news)

    sentiment = SentimentAnalysis(
        news_id=news.id,
        sentiment="positive",
        positive_score=0.94,
        negative_score=0.02,
        neutral_score=0.04,
        confidence=0.94,
        relevance_score=0.98,
        model_name="ProsusAI/finbert"
    )
    db_session.add(sentiment)
    await db_session.commit()
    await db_session.refresh(sentiment)

    assert sentiment.id is not None
    assert sentiment.news_id == news.id
    assert sentiment.sentiment == "positive"

