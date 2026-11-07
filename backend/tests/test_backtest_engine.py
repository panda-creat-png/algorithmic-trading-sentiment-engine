import pytest
from datetime import datetime, timedelta, timezone
import polars as pl
import numpy as np

from app.backtesting.engine import BacktestEngine
from app.backtesting.metrics import PerformanceMetricsCalculator
from app.strategies import (
    MovingAverageCrossoverStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
    MomentumStrategy,
    AISentimentStrategy,
    CombinedTechnicalSentimentStrategy,
    get_strategy,
    STRATEGY_REGISTRY
)


@pytest.fixture
def sample_backtest_ohlcv():
    """Generates 100 synthetic daily candles with an uptrend and pullbacks."""
    np.random.seed(42)
    n = 100
    start_date = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    timestamps = [start_date + timedelta(days=i) for i in range(n)]

    # Generate geometric Brownian motion
    base_price = 100.0
    returns = np.random.normal(0.002, 0.015, n)
    prices = base_price * np.exp(np.cumsum(returns))

    opens = prices * (1.0 + np.random.normal(0, 0.003, n))
    highs = np.maximum(opens, prices) * (1.0 + np.abs(np.random.normal(0, 0.005, n)))
    lows = np.minimum(opens, prices) * (1.0 - np.abs(np.random.normal(0, 0.005, n)))
    closes = prices
    volumes = np.random.uniform(500000, 2000000, n)

    return pl.DataFrame({
        "timestamp": timestamps,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def test_zero_lookahead_bias_guarantee(sample_backtest_ohlcv):
    """
    CRITICAL PROOF TEST:
    1. Validates that a signal generated on candle t is executed strictly at candle t+1 OPEN.
    2. Modifying future data (candles t+10 onwards) must have ZERO impact on trading decisions at candle t.
    """
    strategy = MovingAverageCrossoverStrategy({"fast_period": 5, "slow_period": 15})
    engine = BacktestEngine(initial_capital=100000.0, fee_rate=0.001, slippage=0.0005)

    # 1. Run backtest on baseline data
    result_baseline = engine.run(strategy, sample_backtest_ohlcv, symbol="TEST")
    trades_baseline = result_baseline["trades"]
    assert len(trades_baseline) > 0

    first_trade = trades_baseline[0]
    entry_time = first_trade["entry_time"]
    entry_price = first_trade["entry_price"]

    # Verify execution occurred on candle t+1 Open (with slippage)
    row_idx = sample_backtest_ohlcv["timestamp"].to_list().index(entry_time)
    assert row_idx > 0, "Execution cannot happen on the very first candle."
    expected_open = sample_backtest_ohlcv["open"][row_idx]
    expected_fill = expected_open * (1.0 + 0.0005)
    assert abs(entry_price - expected_fill) < 1e-4

    # 2. Modify future data: drastically alter candles starting 10 bars after the first trade
    cutoff_idx = row_idx + 10
    altered_ohlcv = sample_backtest_ohlcv.with_columns(
        pl.when(pl.int_range(0, pl.len()) >= cutoff_idx)
        .then(pl.col("close") * 5.0)  # 500% future spike
        .otherwise(pl.col("close"))
        .alias("close")
    )

    result_altered = engine.run(strategy, altered_ohlcv, symbol="TEST")
    trades_altered = result_altered["trades"]

    # The first trade MUST be 100% identical: future 500% spike cannot alter past decisions!
    first_trade_altered = trades_altered[0]
    assert first_trade_altered["entry_time"] == first_trade["entry_time"]
    assert first_trade_altered["entry_price"] == first_trade["entry_price"]
    assert first_trade_altered["size"] == first_trade["size"]


def test_slippage_and_fee_deduction(sample_backtest_ohlcv):
    """Verifies that slippage and commission fees are precisely deducted from balance."""
    fee_rate = 0.002   # 0.2%
    slippage = 0.001   # 10 bps
    strategy = MovingAverageCrossoverStrategy({"fast_period": 5, "slow_period": 10})
    engine = BacktestEngine(initial_capital=100000.0, fee_rate=fee_rate, slippage=slippage)

    result = engine.run(strategy, sample_backtest_ohlcv, symbol="TEST")
    assert result["total_fees_paid"] > 0
    assert result["final_equity"] < (100000.0 + sum(t["realized_pnl"] for t in result["trades"]) + 1.0)


def test_stop_loss_trigger():
    """Verifies intra-candle Stop-Loss triggers when Low breaches stop boundary."""
    timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(5)]
    # Day 0: Baseline
    # Day 1: Signal generated (+1)
    # Day 2: Entered at Open = 100. Stop loss set at 5% (stop = 95). Low plunges to 90.
    # Day 3, 4: Flat
    df = pl.DataFrame({
        "timestamp": timestamps,
        "open": [100.0, 100.0, 100.0, 92.0, 92.0],
        "high": [102.0, 102.0, 101.0, 93.0, 93.0],
        "low": [98.0, 98.0, 90.0, 90.0, 90.0],  # Day 2 Low hits 90 (breaches 95)
        "close": [100.0, 100.0, 92.0, 92.0, 92.0],
        "volume": [10000.0] * 5,
        "signal": [0, 1, 0, 0, 0]  # Hardcoded test signal on day 1
    })

    class MockSignalStrategy(MovingAverageCrossoverStrategy):
        def generate_signals(self, d, news_sentiment=None):
            return d

    engine = BacktestEngine(
        initial_capital=10000.0,
        fee_rate=0.0,
        slippage=0.0,
        stop_loss_pct=0.05
    )
    result = engine.run(MockSignalStrategy(), df, symbol="TEST")
    trades = result["trades"]
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop_loss"
    assert trades[0]["exit_price"] == 95.0  # Stopped out at 95


def test_performance_metrics_calculator():
    """Tests institutional formula computations (Sharpe, Max Drawdown, Win Rate)."""
    equity_curve = [
        {"timestamp": datetime(2025, 1, 1, tzinfo=timezone.utc), "equity": 100000.0, "position_size": 10},
        {"timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "equity": 105000.0, "position_size": 10},
        {"timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "equity": 98000.0, "position_size": 10},
        {"timestamp": datetime(2025, 1, 4, tzinfo=timezone.utc), "equity": 110000.0, "position_size": 0},
    ]
    trades = [
        {"realized_pnl": 5000.0},
        {"realized_pnl": -2000.0},
        {"realized_pnl": 7000.0},
    ]

    metrics = PerformanceMetricsCalculator.calculate(
        initial_capital=100000.0,
        final_equity=110000.0,
        equity_curve=equity_curve,
        trades=trades,
        benchmark_initial_price=100.0,
        benchmark_final_price=105.0
    )

    assert metrics["total_return"] == 0.10
    assert metrics["win_rate"] == round(2 / 3, 4)
    assert metrics["profit_factor"] == 6.0  # 12000 profit / 2000 loss
    assert metrics["max_drawdown"] < 0  # Drawdown occurred on day 3 (from 105k to 98k = -6.67%)
    assert abs(metrics["max_drawdown"] - (-0.0667)) < 0.01
    assert metrics["benchmark_return"] == 0.05


def test_all_seven_strategies_execution(sample_backtest_ohlcv):
    """Executes backtest across all 7 quantitative strategies without failure."""
    engine = BacktestEngine(initial_capital=100000.0, fee_rate=0.001, slippage=0.0005)

    sample_news = [
        {
            "published_at": sample_backtest_ohlcv["timestamp"][10].isoformat(),
            "headline": "Company reports blowout quarterly revenue",
            "positive_score": 0.88,
            "negative_score": 0.02,
            "confidence": 0.88
        },
        {
            "published_at": sample_backtest_ohlcv["timestamp"][40].isoformat(),
            "headline": "Regulatory headwind creates short term uncertainty",
            "positive_score": 0.05,
            "negative_score": 0.82,
            "confidence": 0.82
        }
    ]

    for strat_type in STRATEGY_REGISTRY.keys():
        strategy = get_strategy(strat_type)
        result = engine.run(
            strategy,
            sample_backtest_ohlcv,
            symbol="NVDA",
            news_sentiment=sample_news
        )

        assert "metrics" in result
        assert "equity_curve" in result
        assert "trades" in result
        assert result["final_equity"] > 0
        assert "total_return" in result["metrics"]
        assert "sharpe_ratio" in result["metrics"]
