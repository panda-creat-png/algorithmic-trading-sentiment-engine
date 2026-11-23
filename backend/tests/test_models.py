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


@pytest.mark.asyncio
async def test_sqlite_concurrency_and_busy_timeout(tmp_path):
    """Verifies ISS-05 fix: Disk-based SQLite in WAL mode with busy_timeout=30000 executes concurrent transactions without database is locked errors."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy import event, select, text
    from app.models.base import Base

    db_file = tmp_path / "test_concurrency.db"
    url = f"sqlite+aiosqlite:///{db_file}"

    disk_engine = create_async_engine(
        url,
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )

    @event.listens_for(disk_engine.sync_engine, "connect")
    def set_pragmas(dbapi_conn, record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    async with disk_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        res_wal = await conn.execute(text("PRAGMA journal_mode;"))
        assert res_wal.scalar() == "wal"
        res_timeout = await conn.execute(text("PRAGMA busy_timeout;"))
        assert res_timeout.scalar() == 30000

    DiskSessionLocal = async_sessionmaker(bind=disk_engine, class_=AsyncSession, expire_on_commit=False)

    async def insert_worker(i: int):
        async with DiskSessionLocal() as s:
            a = Asset(symbol=f"CONC_{i}", name=f"Concurrency {i}", asset_class="stock", exchange="NASDAQ", currency="USD")
            s.add(a)
            await s.commit()

    # Run 5 concurrent writes on disk SQLite
    await asyncio.gather(*[insert_worker(i) for i in range(5)])

    # Verify all were inserted
    async with DiskSessionLocal() as s:
        res = await s.execute(select(Asset).where(Asset.symbol.startswith("CONC_")))
        assert len(res.scalars().all()) == 5

    await disk_engine.dispose()

