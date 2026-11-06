import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.asset import Asset
from app.models.market_data import MarketData
from app.data_pipeline.yahoo_provider import yahoo_provider
from app.data_pipeline.crypto_provider import crypto_provider
from app.data_pipeline.data_cache import data_cache_service
from app.data_pipeline.validation import validation_service
from app.core.logging import logger

DEFAULT_ASSETS = [
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "AAPL", "name": "Apple Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "BTC-USD", "name": "Bitcoin USD", "asset_class": "crypto", "exchange": "CRYPTO", "currency": "USD"},
    {"symbol": "ETH-USD", "name": "Ethereum USD", "asset_class": "crypto", "exchange": "CRYPTO", "currency": "USD"},
]


class MarketDataService:
    """Core market data orchestration and ingestion service."""

    @staticmethod
    async def seed_default_assets(db: AsyncSession) -> int:
        """Seeds default tracked assets if not present."""
        created_count = 0
        for item in DEFAULT_ASSETS:
            stmt = select(Asset).where(Asset.symbol == item["symbol"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                asset = Asset(**item)
                db.add(asset)
                created_count += 1
        
        if created_count > 0:
            await db.commit()
            logger.info(f"Seeded {created_count} default tracked assets.")
        return created_count

    @staticmethod
    async def get_all_assets(db: AsyncSession) -> List[Asset]:
        """Retrieves all tracked assets."""
        stmt = select(Asset).where(Asset.is_active == True).order_by(Asset.symbol)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_asset_by_symbol(db: AsyncSession, symbol: str) -> Optional[Asset]:
        """Looks up an asset by its ticker symbol."""
        stmt = select(Asset).where(Asset.symbol == symbol.upper())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_quote(cls, symbol: str) -> Dict[str, Any]:
        """Gets live quote from cache or fetches from provider."""
        sym_clean = symbol.upper()
        # 1. Try cache
        cached = await data_cache_service.get_quote(sym_clean)
        if cached:
            cached["cached"] = True
            return cached

        # 2. Provider fetch
        if sym_clean in ("BTC", "BTC-USD", "ETH", "ETH-USD", "SOL", "SOL-USD"):
            quote = await crypto_provider.get_latest_quote(sym_clean)
        else:
            quote = await yahoo_provider.get_latest_quote(sym_clean)

        quote["cached"] = False
        await data_cache_service.set_quote(sym_clean, quote)
        return quote

    @classmethod
    async def get_historical_candles(
        cls,
        db: AsyncSession,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Retrieves historical OHLCV data using Cache -> Database -> Real Provider Ingestion hierarchy."""
        sym_clean = symbol.upper()

        # 1. Check Redis Cache
        if not force_refresh:
            cached_candles = await data_cache_service.get_candles(sym_clean, timeframe, limit)
            if cached_candles and len(cached_candles) > 0:
                return {
                    "symbol": sym_clean,
                    "timeframe": timeframe,
                    "source": "cache",
                    "total_candles": len(cached_candles),
                    "candles": cached_candles,
                }

        # 2. Find or register Asset
        asset = await cls.get_asset_by_symbol(db, sym_clean)
        if not asset:
            asset = Asset(
                symbol=sym_clean,
                name=sym_clean,
                asset_class="crypto" if ("-USD" in sym_clean or sym_clean in ("BTC", "ETH")) else "stock",
                exchange="CRYPTO" if "-USD" in sym_clean else "US",
                currency="USD"
            )
            db.add(asset)
            await db.commit()
            await db.refresh(asset)

        # 3. Check Database for existing candles
        stmt = (
            select(MarketData)
            .where(and_(MarketData.asset_id == asset.id, MarketData.timeframe == timeframe))
            .order_by(MarketData.timestamp.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        db_candles = list(res.scalars().all())

        # If DB has enough recent candles and no refresh forced, return them
        if not force_refresh and len(db_candles) >= min(limit, 20):
            # Sort chronologically ascending
            db_candles.reverse()
            candles_payload = [
                {
                    "timestamp": c.timestamp.isoformat(),
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume,
                    "trades_count": c.trades_count,
                    "vwap": c.vwap,
                }
                for c in db_candles
            ]
            await data_cache_service.set_candles(sym_clean, timeframe, limit, candles_payload)
            return {
                "symbol": sym_clean,
                "timeframe": timeframe,
                "source": "database",
                "total_candles": len(candles_payload),
                "candles": candles_payload,
            }

        # 4. Fetch Live Data from Provider
        logger.info(f"Ingesting real historical data for {sym_clean} ({timeframe}) from provider...")
        provider = crypto_provider if asset.asset_class == "crypto" else yahoo_provider
        
        try:
            pl_df = await provider.fetch_ohlcv(sym_clean, timeframe=timeframe, limit=limit)
        except Exception as e:
            logger.error(f"Provider fetch error for {sym_clean}: {e}")
            # If provider fails, fallback to whatever we have in DB
            if db_candles:
                db_candles.reverse()
                return {
                    "symbol": sym_clean,
                    "timeframe": timeframe,
                    "source": "database_stale_fallback",
                    "total_candles": len(db_candles),
                    "candles": [
                        {
                            "timestamp": c.timestamp.isoformat(),
                            "open": c.open,
                            "high": c.high,
                            "low": c.low,
                            "close": c.close,
                            "volume": c.volume,
                            "vwap": c.vwap,
                        } for c in db_candles
                    ],
                }
            raise

        if pl_df.is_empty():
            return {
                "symbol": sym_clean,
                "timeframe": timeframe,
                "source": "provider_empty",
                "total_candles": 0,
                "candles": [],
            }

        # 5. Convert Polars records & Persist incrementally to DB
        candles_payload = []
        new_records: List[MarketData] = []
        
        for row in pl_df.iter_rows(named=True):
            ts = row["timestamp"]
            # Convert to python datetime
            if hasattr(ts, "to_pydatetime"):
                ts = ts.to_pydatetime()
            elif isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            
            candle_dict = {
                "timestamp": ts.isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "vwap": float(row["vwap"]) if row.get("vwap") is not None else None,
            }
            candles_payload.append(candle_dict)

            # Check if already in DB to prevent constraint violation
            existing_stmt = select(MarketData.id).where(
                and_(
                    MarketData.asset_id == asset.id,
                    MarketData.timeframe == timeframe,
                    MarketData.timestamp == ts
                )
            )
            ex_res = await db.execute(existing_stmt)
            if not ex_res.scalar_one_or_none():
                new_records.append(
                    MarketData(
                        asset_id=asset.id,
                        timeframe=timeframe,
                        timestamp=ts,
                        open=candle_dict["open"],
                        high=candle_dict["high"],
                        low=candle_dict["low"],
                        close=candle_dict["close"],
                        volume=candle_dict["volume"],
                        vwap=candle_dict["vwap"],
                    )
                )

        if new_records:
            db.add_all(new_records)
            await db.commit()
            logger.info(f"Persisted {len(new_records)} new candles for {sym_clean} ({timeframe})")

        # 6. Save in Cache
        await data_cache_service.set_candles(sym_clean, timeframe, limit, candles_payload)

        return {
            "symbol": sym_clean,
            "timeframe": timeframe,
            "source": "provider_live",
            "total_candles": len(candles_payload),
            "candles": candles_payload,
        }


market_data_service = MarketDataService()
