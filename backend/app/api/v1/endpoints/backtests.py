from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import polars as pl

from app.core.database import get_db
from app.models.backtest import BacktestRun, BacktestTrade
from app.models.strategy import TradingStrategy
from app.models.asset import Asset
from app.models.sentiment import SentimentAnalysis
from app.schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestMetrics,
    TradeResponse
)
from app.services.market_data_service import market_data_service
from app.strategies import get_strategy
from app.backtesting.engine import BacktestEngine
from app.core.logging import logger

router = APIRouter()


def ensure_datetime(val) -> datetime:
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except Exception:
            pass
    if hasattr(val, "to_pydatetime"):
        dt = val.to_pydatetime()
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


@router.post("/run", response_model=BacktestResponse, status_code=200, summary="Execute Event-Driven Backtest")
async def run_backtest(payload: BacktestRequest, db: AsyncSession = Depends(get_db)):
    """
    Executes an institutional event-driven backtesting simulation.
    Guarantees zero look-ahead bias: orders triggered at candle t close are executed at candle t+1 Open.
    """
    sym_clean = payload.symbol.upper()

    # 1. Ensure asset exists in DB
    asset = await market_data_service.get_asset_by_symbol(db, sym_clean)
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

    # 2. Retrieve or identify strategy
    strategy_rec = None
    if payload.strategy_id:
        stmt = select(TradingStrategy).where(TradingStrategy.id == payload.strategy_id)
        result = await db.execute(stmt)
        strategy_rec = result.scalar_one_or_none()

    strategy_type = payload.strategy_type or (strategy_rec.strategy_type if strategy_rec else "ma_crossover")
    strategy_params = {}
    if strategy_rec and strategy_rec.parameters:
        strategy_params.update(strategy_rec.parameters)
    if payload.parameters:
        strategy_params.update(payload.parameters)

    # 3. Retrieve historical candle data (180 to 365 bars)
    limit = 300
    history_res = await market_data_service.get_historical_candles(
        db=db,
        symbol=sym_clean,
        timeframe=payload.timeframe,
        limit=limit
    )

    candles_data = history_res.get("candles", [])
    if len(candles_data) < 15:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient historical data for {sym_clean} ({len(candles_data)} candles). Minimum 15 required."
        )

    # Convert to Polars DataFrame
    ohlcv_df = pl.DataFrame(candles_data)

    # Filter date range if provided
    start_date = payload.start_date
    end_date = payload.end_date

    if start_date:
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        ohlcv_df = ohlcv_df.filter(pl.col("timestamp") >= start_date)

    if end_date:
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        ohlcv_df = ohlcv_df.filter(pl.col("timestamp") <= end_date)

    if ohlcv_df.height < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient candles within the specified date range ({ohlcv_df.height} bars)."
        )

    # 4. If AI Sentiment strategy or Combined strategy, fetch historical sentiment records
    news_sentiment_feed = []
    if strategy_type in ("sentiment", "combined"):
        stmt = (
            select(SentimentAnalysis)
            .where(SentimentAnalysis.asset_id == asset.id)
            .order_by(SentimentAnalysis.created_at)
        )
        res = await db.execute(stmt)
        sentiment_records = res.scalars().all()
        for s in sentiment_records:
            news_sentiment_feed.append({
                "published_at": s.created_at,
                "positive_score": s.positive_score,
                "negative_score": s.negative_score,
                "confidence": s.confidence,
            })

    # 5. Instantiate Strategy and BacktestEngine
    try:
        strategy = get_strategy(strategy_type, parameters=strategy_params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to instantiate strategy: {str(e)}")

    engine = BacktestEngine(
        initial_capital=payload.initial_capital,
        fee_rate=payload.fee_rate,
        slippage=payload.slippage,
        stop_loss_pct=payload.stop_loss_pct,
        take_profit_pct=payload.take_profit_pct
    )

    # 6. Execute Simulation (Zero Look-Ahead Bias)
    sim_result = engine.run(
        strategy=strategy,
        ohlcv_df=ohlcv_df,
        symbol=sym_clean,
        news_sentiment=news_sentiment_feed
    )

    computed_metrics = sim_result["metrics"]
    metrics_schema = BacktestMetrics(**computed_metrics)

    # 7. Persist BacktestRun and BacktestTrade in DB
    run_start = ensure_datetime(ohlcv_df["timestamp"][0])
    run_end = ensure_datetime(ohlcv_df["timestamp"][-1])

    # Ensure strategy in DB for FK
    db_strat_id = strategy_rec.id if strategy_rec else None
    if not db_strat_id:
        stmt = select(TradingStrategy).where(TradingStrategy.strategy_type == strategy_type)
        res = await db.execute(stmt)
        first_strat = res.scalar_one_or_none()
        if first_strat:
            db_strat_id = first_strat.id
        else:
            new_strat = TradingStrategy(
                name=strategy.name,
                strategy_type=strategy_type,
                parameters=strategy_params
            )
            db.add(new_strat)
            await db.commit()
            await db.refresh(new_strat)
            db_strat_id = new_strat.id

    backtest_record = BacktestRun(
        strategy_id=db_strat_id,
        asset_id=asset.id,
        start_date=run_start,
        end_date=run_end,
        timeframe=payload.timeframe,
        initial_capital=payload.initial_capital,
        final_equity=sim_result["final_equity"],
        total_return=computed_metrics.get("total_return"),
        cagr=computed_metrics.get("cagr"),
        sharpe_ratio=computed_metrics.get("sharpe_ratio"),
        sortino_ratio=computed_metrics.get("sortino_ratio"),
        max_drawdown=computed_metrics.get("max_drawdown"),
        calmar_ratio=computed_metrics.get("calmar_ratio"),
        win_rate=computed_metrics.get("win_rate"),
        profit_factor=computed_metrics.get("profit_factor"),
        total_trades=computed_metrics.get("total_trades"),
        annualized_volatility=computed_metrics.get("annualized_volatility"),
        exposure_time=computed_metrics.get("exposure_time"),
        parameters=strategy_params,
        status="completed"
    )
    db.add(backtest_record)
    await db.commit()
    await db.refresh(backtest_record)

    # Persist trades
    trade_responses: List[TradeResponse] = []
    for t in sim_result["trades"]:
        entry_t = ensure_datetime(t["entry_time"])
        exit_t = ensure_datetime(t["exit_time"])

        trade_record = BacktestTrade(
            backtest_id=backtest_record.id,
            symbol=sym_clean,
            side=t["side"],
            entry_time=entry_t,
            exit_time=exit_t,
            entry_price=t["entry_price"],
            exit_price=t["exit_price"],
            size=t["size"],
            fee=t["fee"],
            slippage=t["slippage"],
            realized_pnl=t["realized_pnl"],
            pnl_percentage=t["pnl_percentage"],
            exit_reason=t["exit_reason"]
        )
        db.add(trade_record)
        trade_responses.append(TradeResponse(
            id=t["id"],
            symbol=sym_clean,
            side=t["side"],
            entry_time=entry_t,
            exit_time=exit_t,
            entry_price=t["entry_price"],
            exit_price=t["exit_price"],
            size=t["size"],
            fee=t["fee"],
            slippage=t["slippage"],
            realized_pnl=t["realized_pnl"],
            pnl_percentage=t["pnl_percentage"],
            exit_reason=t["exit_reason"]
        ))

    await db.commit()

    return BacktestResponse(
        id=backtest_record.id,
        strategy_id=db_strat_id,
        asset_id=asset.id,
        symbol=sym_clean,
        status="completed",
        start_date=run_start,
        end_date=run_end,
        timeframe=payload.timeframe,
        initial_capital=payload.initial_capital,
        final_equity=sim_result["final_equity"],
        total_fees_paid=sim_result["total_fees_paid"],
        metrics=metrics_schema,
        equity_curve=sim_result["equity_curve"],
        trades=trade_responses,
        error_message=None,
        created_at=backtest_record.created_at
    )


@router.get("", response_model=List[BacktestResponse], summary="List Past Backtest Runs")
async def list_backtests(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Returns past backtest runs ordered by newest first."""
    stmt = select(BacktestRun).order_by(desc(BacktestRun.created_at)).limit(limit)
    result = await db.execute(stmt)
    runs = result.scalars().all()

    responses = []
    for r in runs:
        metrics = BacktestMetrics(
            total_return=r.total_return,
            cagr=r.cagr,
            sharpe_ratio=r.sharpe_ratio,
            sortino_ratio=r.sortino_ratio,
            max_drawdown=r.max_drawdown,
            calmar_ratio=r.calmar_ratio,
            win_rate=r.win_rate,
            profit_factor=r.profit_factor,
            total_trades=r.total_trades or 0,
            annualized_volatility=r.annualized_volatility,
            exposure_time=r.exposure_time
        )
        responses.append(BacktestResponse(
            id=r.id,
            strategy_id=r.strategy_id,
            asset_id=r.asset_id,
            symbol=None,
            status=r.status,
            start_date=r.start_date,
            end_date=r.end_date,
            timeframe=r.timeframe,
            initial_capital=r.initial_capital,
            final_equity=r.final_equity,
            total_fees_paid=0.0,
            metrics=metrics,
            equity_curve=None,
            trades=None,
            error_message=r.error_message,
            created_at=r.created_at
        ))
    return responses


@router.get("/{backtest_id}", response_model=BacktestResponse, summary="Get Backtest Run Details")
async def get_backtest_details(backtest_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches details and performance summary of a specific backtest."""
    stmt = select(BacktestRun).where(BacktestRun.id == backtest_id)
    result = await db.execute(stmt)
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Backtest run not found")

    metrics = BacktestMetrics(
        total_return=r.total_return,
        cagr=r.cagr,
        sharpe_ratio=r.sharpe_ratio,
        sortino_ratio=r.sortino_ratio,
        max_drawdown=r.max_drawdown,
        calmar_ratio=r.calmar_ratio,
        win_rate=r.win_rate,
        profit_factor=r.profit_factor,
        total_trades=r.total_trades or 0,
        annualized_volatility=r.annualized_volatility,
        exposure_time=r.exposure_time
    )

    # Fetch trades
    stmt_trades = select(BacktestTrade).where(BacktestTrade.backtest_id == backtest_id)
    t_res = await db.execute(stmt_trades)
    trades = [
        TradeResponse(
            id=t.id,
            symbol=t.symbol,
            side=t.side,
            entry_time=t.entry_time,
            exit_time=t.exit_time,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            size=t.size,
            fee=t.fee,
            slippage=t.slippage,
            realized_pnl=t.realized_pnl,
            pnl_percentage=t.pnl_percentage,
            exit_reason=t.exit_reason
        )
        for t in t_res.scalars().all()
    ]

    return BacktestResponse(
        id=r.id,
        strategy_id=r.strategy_id,
        asset_id=r.asset_id,
        symbol=None,
        status=r.status,
        start_date=r.start_date,
        end_date=r.end_date,
        timeframe=r.timeframe,
        initial_capital=r.initial_capital,
        final_equity=r.final_equity,
        total_fees_paid=0.0,
        metrics=metrics,
        equity_curve=None,
        trades=trades,
        error_message=r.error_message,
        created_at=r.created_at
    )


@router.get("/{backtest_id}/trades", response_model=List[TradeResponse], summary="Get Backtest Trades")
async def get_backtest_trades(backtest_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches all individual trades executed during the backtest."""
    stmt = select(BacktestTrade).where(BacktestTrade.backtest_id == backtest_id).order_by(BacktestTrade.entry_time)
    result = await db.execute(stmt)
    trades = result.scalars().all()
    return [
        TradeResponse(
            id=t.id,
            symbol=t.symbol,
            side=t.side,
            entry_time=t.entry_time,
            exit_time=t.exit_time,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            size=t.size,
            fee=t.fee,
            slippage=t.slippage,
            realized_pnl=t.realized_pnl,
            pnl_percentage=t.pnl_percentage,
            exit_reason=t.exit_reason
        )
        for t in trades
    ]
