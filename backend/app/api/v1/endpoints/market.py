from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.market_data_service import market_data_service
from app.schemas.market import AssetResponse, MarketHistoryResponse, IndicatorResponse

router = APIRouter()


@router.get("/assets", response_model=List[AssetResponse], summary="List Tracked Assets")
async def list_assets(db: AsyncSession = Depends(get_db)):
    """Returns all tracked assets in the platform."""
    assets = await market_data_service.get_all_assets(db)
    if not assets:
        await market_data_service.seed_default_assets(db)
        assets = await market_data_service.get_all_assets(db)
    return assets


@router.get("/{symbol}/history", response_model=MarketHistoryResponse, summary="Get Historical OHLCV Data")
async def get_market_history(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe candle interval: 1m, 5m, 15m, 1h, 4h, 1d, 1wk"),
    limit: int = Query(100, ge=1, le=1000, description="Max candles to return"),
    db: AsyncSession = Depends(get_db)
):
    """Returns validated historical OHLCV candles for the specified symbol."""
    asset = await market_data_service.get_asset_by_symbol(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset symbol {symbol.upper()} not found.")
    
    # In Phase 1 initial setup, return structural historical response
    return MarketHistoryResponse(
        symbol=symbol.upper(),
        timeframe=timeframe,
        total_candles=0,
        candles=[]
    )


@router.get("/{symbol}/indicators", response_model=List[IndicatorResponse], summary="Get Technical Indicators")
async def get_market_indicators(
    symbol: str,
    indicator: Optional[str] = Query(None, description="Specific indicator: SMA_20, EMA_12, RSI_14, MACD, etc."),
    db: AsyncSession = Depends(get_db)
):
    """Returns computed technical indicators for the specified symbol."""
    asset = await market_data_service.get_asset_by_symbol(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset symbol {symbol.upper()} not found.")
    return []

