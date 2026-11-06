from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.market_data_service import market_data_service
from app.schemas.market import (
    AssetResponse,
    MarketHistoryResponse,
    MarketQuoteResponse,
    SyncAssetsRequest,
    IndicatorResponse,
)
from app.core.logging import logger

router = APIRouter()


@router.get("/assets", response_model=List[AssetResponse], summary="List Tracked Assets")
async def list_assets(db: AsyncSession = Depends(get_db)):
    """Returns all tracked assets in the platform, auto-seeding default universe if empty."""
    assets = await market_data_service.get_all_assets(db)
    if not assets:
        await market_data_service.seed_default_assets(db)
        assets = await market_data_service.get_all_assets(db)
    return assets


@router.get("/{symbol}/quote", response_model=MarketQuoteResponse, summary="Get Live Real-time Quote")
async def get_live_quote(symbol: str):
    """Fetches real-time market quote including price, 24h change, day high/low, and volume."""
    try:
        quote = await market_data_service.get_quote(symbol)
        return MarketQuoteResponse(**quote)
    except Exception as e:
        logger.error(f"Quote error for {symbol}: {e}")
        raise HTTPException(status_code=502, detail=f"Unable to fetch quote for {symbol.upper()}: {str(e)}")


@router.get("/{symbol}/history", response_model=MarketHistoryResponse, summary="Get Historical OHLCV Data")
async def get_market_history(
    symbol: str,
    timeframe: str = Query("1d", description="Candle interval: 1m, 5m, 15m, 1h, 4h, 1d, 1wk"),
    limit: int = Query(100, ge=1, le=1000, description="Max candles to return"),
    refresh: bool = Query(False, description="Force live provider fetch bypassing cache"),
    db: AsyncSession = Depends(get_db)
):
    """Returns validated historical OHLCV market candles from cache/database/real provider pipeline."""
    try:
        res = await market_data_service.get_historical_candles(
            db=db,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            force_refresh=refresh
        )
        return MarketHistoryResponse(**res)
    except Exception as e:
        logger.error(f"History fetch error for {symbol}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to ingest market data for {symbol.upper()}: {str(e)}")


@router.post("/sync", summary="Trigger Market Data Sync")
async def sync_market_data(
    payload: SyncAssetsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Triggers background data ingestion and validation for tracked assets."""
    target_symbols = payload.symbols
    if not target_symbols:
        assets = await market_data_service.get_all_assets(db)
        target_symbols = [a.symbol for a in assets]

    async def _sync_symbols(symbols: List[str], tf: str, lim: int):
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            for s in symbols:
                try:
                    await market_data_service.get_historical_candles(
                        db=session,
                        symbol=s,
                        timeframe=tf,
                        limit=lim,
                        force_refresh=True
                    )
                except Exception as err:
                    logger.warning(f"Background sync failed for {s}: {err}")

    background_tasks.add_task(_sync_symbols, target_symbols, payload.timeframe, payload.limit)
    return {
        "status": "sync_scheduled",
        "symbols_count": len(target_symbols),
        "timeframe": payload.timeframe,
        "limit": payload.limit,
    }


@router.get("/{symbol}/indicators", response_model=List[IndicatorResponse], summary="Get Technical Indicators")
async def get_market_indicators(
    symbol: str,
    indicator: Optional[str] = Query(None, description="Specific indicator: SMA_20, EMA_12, RSI_14, MACD, etc."),
    db: AsyncSession = Depends(get_db)
):
    """Returns computed technical indicators for the specified symbol."""
    return []
