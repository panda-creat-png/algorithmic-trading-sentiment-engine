from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.strategy import TradingStrategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse

router = APIRouter()

PREBUILT_STRATEGIES = [
    {
        "name": "Dual Moving Average Crossover",
        "description": "Golden Cross / Death Cross using 20 and 50 period SMA with ATR stop-loss.",
        "strategy_type": "ma_crossover",
        "parameters": {"fast_period": 20, "slow_period": 50, "stop_loss_pct": 0.02, "take_profit_pct": 0.05}
    },
    {
        "name": "RSI Mean Reversion",
        "description": "Buys oversold conditions (RSI < 30) and sells overbought (RSI > 70).",
        "strategy_type": "rsi_reversal",
        "parameters": {"rsi_period": 14, "oversold": 30, "overbought": 70}
    },
    {
        "name": "MACD Trend Momentum",
        "description": "Enters trades when MACD histogram crosses zero line with confirmation.",
        "strategy_type": "macd",
        "parameters": {"fast": 12, "slow": 26, "signal": 9}
    },
    {
        "name": "Bollinger Bands Volatility Breakout",
        "description": "Trades price channel breakouts and standard deviation squeezes.",
        "strategy_type": "bollinger",
        "parameters": {"period": 20, "std_dev": 2.0}
    },
    {
        "name": "AI Sentiment Augmented Momentum",
        "description": "Combines RSI and MACD signals with FinBERT news sentiment confirmation score.",
        "strategy_type": "combined",
        "parameters": {"sentiment_threshold": 0.65, "rsi_threshold": 50}
    }
]


@router.get("", response_model=List[StrategyResponse], summary="List Trading Strategies")
async def list_strategies(db: AsyncSession = Depends(get_db)):
    """Lists all available strategies, initializing prebuilt quant strategies if none exist."""
    stmt = select(TradingStrategy)
    result = await db.execute(stmt)
    strategies = list(result.scalars().all())
    
    if not strategies:
        for item in PREBUILT_STRATEGIES:
            strat = TradingStrategy(**item)
            db.add(strat)
        await db.commit()
        result = await db.execute(stmt)
        strategies = list(result.scalars().all())
    
    return strategies


@router.post("", response_model=StrategyResponse, status_code=201, summary="Create Custom Strategy")
async def create_strategy(payload: StrategyCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new algorithmic trading strategy."""
    strat = TradingStrategy(
        name=payload.name,
        description=payload.description,
        strategy_type=payload.strategy_type,
        is_active=payload.is_active,
        parameters=payload.parameters
    )
    db.add(strat)
    await db.commit()
    await db.refresh(strat)
    return strat


@router.get("/{strategy_id}", response_model=StrategyResponse, summary="Get Strategy by ID")
async def get_strategy(strategy_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches a specific strategy."""
    stmt = select(TradingStrategy).where(TradingStrategy.id == strategy_id)
    result = await db.execute(stmt)
    strat = result.scalar_one_or_none()
    if not strat:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strat


@router.put("/{strategy_id}", response_model=StrategyResponse, summary="Update Strategy")
async def update_strategy(strategy_id: int, payload: StrategyUpdate, db: AsyncSession = Depends(get_db)):
    """Updates strategy parameters or configuration."""
    stmt = select(TradingStrategy).where(TradingStrategy.id == strategy_id)
    result = await db.execute(stmt)
    strat = result.scalar_one_or_none()
    if not strat:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if payload.name is not None:
        strat.name = payload.name
    if payload.description is not None:
        strat.description = payload.description
    if payload.strategy_type is not None:
        strat.strategy_type = payload.strategy_type
    if payload.is_active is not None:
        strat.is_active = payload.is_active
    if payload.parameters is not None:
        strat.parameters = payload.parameters

    await db.commit()
    await db.refresh(strat)
    return strat


@router.delete("/{strategy_id}", summary="Delete Strategy")
async def delete_strategy(strategy_id: int, db: AsyncSession = Depends(get_db)):
    """Deletes a custom trading strategy."""
    stmt = select(TradingStrategy).where(TradingStrategy.id == strategy_id)
    result = await db.execute(stmt)
    strat = result.scalar_one_or_none()
    if not strat:
        raise HTTPException(status_code=404, detail="Strategy not found")
    await db.delete(strat)
    await db.commit()
    return {"message": "Strategy deleted successfully", "id": strategy_id}

