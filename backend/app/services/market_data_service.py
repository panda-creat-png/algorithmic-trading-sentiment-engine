from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset
from app.core.logging import logger

DEFAULT_ASSETS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "asset_class": "stock", "exchange": "NASDAQ", "currency": "USD"},
    {"symbol": "BTC-USD", "name": "Bitcoin USD", "asset_class": "crypto", "exchange": "CRYPTO", "currency": "USD"},
    {"symbol": "ETH-USD", "name": "Ethereum USD", "asset_class": "crypto", "exchange": "CRYPTO", "currency": "USD"},
]


class MarketDataService:
    """Core market data orchestration service."""

    @staticmethod
    async def seed_default_assets(db: AsyncSession) -> int:
        """Seeds default blue-chip and crypto assets if not present."""
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


market_data_service = MarketDataService()

