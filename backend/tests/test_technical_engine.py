import pytest
from datetime import datetime, timezone, timedelta
import polars as pl
from app.indicators.technical_engine import technical_engine


@pytest.fixture
def sample_ohlcv_df() -> pl.DataFrame:
    """Generates synthetic deterministic trended OHLCV series for quantitative tests."""
    n = 60
    base_time = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    timestamps = [base_time + timedelta(days=i) for i in range(n)]

    # Upward trend price series
    prices = [100.0 + (i * 0.5) + (2.0 if i % 2 == 0 else -1.0) for i in range(n)]
    opens = [p - 0.2 for p in prices]
    highs = [p + 1.5 for p in prices]
    lows = [p - 1.2 for p in prices]
    closes = prices
    volumes = [100000.0 + (i * 1000) for i in range(n)]

    return pl.DataFrame({
        "timestamp": timestamps,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def test_sma_and_ema_calculation(sample_ohlcv_df: pl.DataFrame):
    df_ind = technical_engine.compute_all_indicators(sample_ohlcv_df)
    assert "sma_20" in df_ind.columns
    assert "sma_50" in df_ind.columns
    assert "ema_12" in df_ind.columns
    assert "ema_26" in df_ind.columns

    # Verify SMA 20 on row 25 is positive and close to average
    sma_20_val = df_ind["sma_20"][25]
    assert sma_20_val is not None
    assert sma_20_val > 90.0


def test_rsi_bounds(sample_ohlcv_df: pl.DataFrame):
    df_ind = technical_engine.compute_all_indicators(sample_ohlcv_df)
    assert "rsi_14" in df_ind.columns

    rsi_values = df_ind["rsi_14"].to_list()
    for val in rsi_values:
        assert 0.0 <= val <= 100.0


def test_macd_and_histogram(sample_ohlcv_df: pl.DataFrame):
    df_ind = technical_engine.compute_all_indicators(sample_ohlcv_df)
    assert "macd_line" in df_ind.columns
    assert "macd_signal" in df_ind.columns
    assert "macd_hist" in df_ind.columns

    # In an uptrend, MACD line should be positive
    latest_macd = df_ind["macd_line"][-1]
    assert latest_macd > 0


def test_bollinger_bands_geometry(sample_ohlcv_df: pl.DataFrame):
    df_ind = technical_engine.compute_all_indicators(sample_ohlcv_df)
    assert "bb_upper" in df_ind.columns
    assert "bb_middle" in df_ind.columns
    assert "bb_lower" in df_ind.columns

    for row in df_ind.iter_rows(named=True):
        if row["bb_upper"] is not None and row["bb_lower"] is not None:
            assert row["bb_upper"] >= row["bb_middle"]
            assert row["bb_middle"] >= row["bb_lower"]


def test_atr_positive(sample_ohlcv_df: pl.DataFrame):
    df_ind = technical_engine.compute_all_indicators(sample_ohlcv_df)
    assert "atr_14" in df_ind.columns
    atr_vals = df_ind["atr_14"].to_list()
    assert all(a >= 0.0 for a in atr_vals)


def test_signal_generation(sample_ohlcv_df: pl.DataFrame):
    signals = technical_engine.generate_signals(sample_ohlcv_df)
    assert signals["status"] == "computed"
    assert "net_score" in signals
    assert "bias" in signals
    assert signals["bias"] in ("BULLISH", "BEARISH", "NEUTRAL")
    assert "latest_metrics" in signals
    assert signals["latest_metrics"]["rsi_14"] > 0

