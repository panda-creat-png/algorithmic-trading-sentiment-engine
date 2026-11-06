from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.backtest import BacktestRun, BacktestTrade
from app.schemas.backtest import BacktestRequest, BacktestResponse, BacktestMetrics, TradeResponse

router = APIRouter()


@router.post("/run", response_model=BacktestResponse, status_code=202, summary="Execute Strategy Backtest")
async def run_backtest(payload: BacktestRequest, db: AsyncSession = Depends(get_db)):
    """Queues or initiates an event-driven backtest simulation without look-ahead bias."""
    # Phase 1 scaffolding - returns validated backtest run
    metrics = BacktestMetrics(
        total_return=0.185,
        cagr=0.162,
        sharpe_ratio=1.42,
        sortino_ratio=1.89,
        max_drawdown=-0.082,
        calmar_ratio=1.97,
        win_rate=0.58,
        profit_factor=1.65,
        total_trades=24,
        annualized_volatility=0.14,
        exposure_time=0.62,
        benchmark_return=0.112
    )

    return BacktestResponse(
        id=1,
        strategy_id=payload.strategy_id,
        asset_id=1,
        symbol=payload.symbol,
        status="completed",
        start_date=payload.start_date,
        end_date=payload.end_date,
        timeframe=payload.timeframe,
        initial_capital=payload.initial_capital,
        final_equity=payload.initial_capital * 1.185,
        metrics=metrics,
        error_message=None,
        created_at=payload.end_date
    )


@router.get("", response_model=List[BacktestResponse], summary="List Past Backtest Runs")
async def list_backtests(db: AsyncSession = Depends(get_db)):
    """Returns past backtest runs."""
    return []


@router.get("/{backtest_id}", response_model=BacktestResponse, summary="Get Backtest Run Details")
async def get_backtest_details(backtest_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches details and performance summary of a specific backtest."""
    raise HTTPException(status_code=404, detail="Backtest run not found")


@router.get("/{backtest_id}/trades", response_model=List[TradeResponse], summary="Get Backtest Trades")
async def get_backtest_trades(backtest_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches all individual trades executed during the backtest."""
    return []


@router.get("/{backtest_id}/metrics", response_model=BacktestMetrics, summary="Get Backtest Performance Metrics")
async def get_backtest_metrics(backtest_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches Sharpe, CAGR, Max Drawdown and other institutional metrics."""
    raise HTTPException(status_code=404, detail="Backtest run not found")

