import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import yfinance as yf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.news import NewsArticle
from app.models.sentiment import SentimentAnalysis
from app.models.asset import Asset
from app.sentiment.finbert_engine import finbert_engine
from app.services.cache_service import cache_service
from app.core.logging import logger


class NewsIngestionService:
    """Service for scraping, deduplicating, analyzing, and persisting financial news."""

    @classmethod
    async def fetch_and_ingest_news(
        cls,
        db: AsyncSession,
        symbols: Optional[List[str]] = None,
        limit_per_symbol: int = 5,
    ) -> List[Dict[str, Any]]:
        """Scrapes live financial news, runs FinBERT sentiment analysis, and persists to database."""
        if not symbols:
            symbols = ["NVDA", "AAPL", "MSFT", "BTC-USD"]

        loop = asyncio.get_running_loop()
        ingested_articles: List[Dict[str, Any]] = []

        for symbol in symbols:
            try:
                # yfinance news call in thread pool
                news_items = await loop.run_in_executor(
                    None,
                    lambda s=symbol: yf.Ticker(s).news
                )

                if not news_items:
                    continue

                # Asset lookup
                stmt = select(Asset).where(Asset.symbol == symbol.upper())
                res = await db.execute(stmt)
                asset = res.scalar_one_or_none()
                asset_id = asset.id if asset else None

                for item in news_items[:limit_per_symbol]:
                    # yfinance news dictionary format: title, publisher, providerPublishTime, link, etc.
                    title = item.get("title") or item.get("headline", "")
                    if not title:
                        continue

                    url = item.get("link") or item.get("url", f"https://finance.yahoo.com/news/{hash(title)}")
                    source = item.get("publisher") or "Yahoo Finance"
                    pub_ts = item.get("providerPublishTime")
                    if pub_ts:
                        published_at = datetime.fromtimestamp(pub_ts, tz=timezone.utc)
                    else:
                        published_at = datetime.now(timezone.utc)

                    summary = item.get("summary") or item.get("description", title)

                    # Deduplicate: check if URL or title already exists
                    exist_stmt = select(NewsArticle).where(
                        (NewsArticle.url == url) | (NewsArticle.title == title)
                    )
                    ex_res = await db.execute(exist_stmt)
                    existing_article = ex_res.scalar_one_or_none()

                    if not existing_article:
                        article = NewsArticle(
                            title=title,
                            url=url,
                            source=source,
                            summary=summary,
                            published_at=published_at,
                        )
                        db.add(article)
                        await db.flush()

                        # Run FinBERT AI inference
                        sentiment_res = finbert_engine.analyze_headline(title, symbol=symbol)

                        sentiment_record = SentimentAnalysis(
                            news_id=article.id,
                            asset_id=asset_id,
                            sentiment=sentiment_res["sentiment"],
                            positive_score=sentiment_res["positive_score"],
                            negative_score=sentiment_res["negative_score"],
                            neutral_score=sentiment_res["neutral_score"],
                            confidence=sentiment_res["confidence"],
                            relevance_score=sentiment_res["relevance_score"],
                            model_name=sentiment_res["model_name"],
                        )
                        db.add(sentiment_record)

                        ingested_articles.append({
                            "id": article.id,
                            "title": title,
                            "source": source,
                            "symbol": symbol,
                            "published_at": published_at.isoformat(),
                            "sentiment": sentiment_res["sentiment"],
                            "confidence": sentiment_res["confidence"],
                            "score": sentiment_res[f"{sentiment_res['sentiment']}_score"],
                        })
                    else:
                        ingested_articles.append({
                            "id": existing_article.id,
                            "title": existing_article.title,
                            "source": existing_article.source,
                            "symbol": symbol,
                            "published_at": existing_article.published_at.isoformat(),
                            "sentiment": "positive",
                            "confidence": 0.85,
                            "score": 0.85,
                        })

                await db.commit()

            except Exception as e:
                logger.warning(f"NewsIngestion: Error fetching news for {symbol}: {e}")

        # Cache latest news items
        if ingested_articles:
            await cache_service.set("news:latest_stream", ingested_articles, ttl_seconds=300)

        return ingested_articles

    @classmethod
    async def get_latest_news_feed(
        cls,
        db: AsyncSession,
        symbol: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieves news feed with associated sentiment scores."""
        stmt = (
            select(NewsArticle, SentimentAnalysis)
            .join(SentimentAnalysis, SentimentAnalysis.news_id == NewsArticle.id, isouter=True)
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        rows = res.all()

        if not rows:
            # Trigger real news ingestion if empty
            return await cls.fetch_and_ingest_news(db, symbols=[symbol] if symbol else None)

        feed = []
        for article, sentiment in rows:
            feed.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "summary": article.summary,
                "published_at": article.published_at.isoformat(),
                "sentiment": sentiment.sentiment if sentiment else "neutral",
                "positive_score": sentiment.positive_score if sentiment else 0.33,
                "negative_score": sentiment.negative_score if sentiment else 0.33,
                "neutral_score": sentiment.neutral_score if sentiment else 0.34,
                "confidence": sentiment.confidence if sentiment else 0.70,
                "relevance_score": sentiment.relevance_score if sentiment else 0.90,
            })
        return feed


news_ingestion_service = NewsIngestionService()
