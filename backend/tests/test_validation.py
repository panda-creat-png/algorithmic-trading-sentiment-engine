import pytest
from datetime import datetime, timezone, timedelta
import polars as pl
from app.data_pipeline.validation import validation_service


def test_validate_ohlc_integrity_clean_data():
    df = pl.DataFrame({
        "timestamp": [
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        ],
        "open": [100.0, 102.0],
        "high": [105.0, 106.0],
        "low": [98.0, 101.0],
        "close": [103.0, 104.0],
        "volume": [1000.0, 1500.0],
    })

    clean_df, report = validation_service.validate_ohlc_integrity(df)
    assert report["is_valid"] is True
    assert report["corrupted_records"] == 0
    assert len(clean_df) == 2


def test_validate_ohlc_integrity_filters_corrupted():
    df = pl.DataFrame({
        "timestamp": [
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),  # Corrupted: High < Low
            datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),  # Corrupted: Volume < 0
        ],
        "open": [100.0, 105.0, 102.0],
        "high": [105.0, 95.0, 106.0],
        "low": [98.0, 100.0, 101.0],
        "close": [103.0, 96.0, 104.0],
        "volume": [1000.0, 500.0, -10.0],
    })

    clean_df, report = validation_service.validate_ohlc_integrity(df)
    assert report["is_valid"] is False
    assert report["corrupted_records"] == 2
    assert len(clean_df) == 1
    assert clean_df["open"][0] == 100.0


def test_deduplicate_timestamps():
    df = pl.DataFrame({
        "timestamp": [
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),  # duplicate
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        ],
        "close": [100.0, 101.0, 102.0],
    })

    dedup = validation_service.deduplicate(df)
    assert len(dedup) == 2
    assert dedup["close"][0] == 101.0  # keeps last


def test_compute_vwap():
    df = pl.DataFrame({
        "timestamp": [
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        ],
        "open": [10.0, 12.0],
        "high": [15.0, 14.0],
        "low": [9.0, 11.0],
        "close": [12.0, 13.0],
        "volume": [100.0, 200.0],
    })

    result = validation_service.compute_vwap(df)
    assert "vwap" in result.columns
    # Row 1 TP = (15 + 9 + 12)/3 = 12. VWAP = 12 * 100 / 100 = 12.0
    assert round(result["vwap"][0], 2) == 12.00
    # Row 2 TP = (14 + 11 + 13)/3 = 12.6667. Cum TP*Vol = 1200 + 2533.33 = 3733.33 / 300 = 12.44
    assert round(result["vwap"][1], 2) == 12.44


def test_detect_missing_gaps():
    df = pl.DataFrame({
        "timestamp": [
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 1, tzinfo=timezone.utc),
            # Gap of 5 minutes between 10:01 and 10:06
            datetime(2026, 1, 1, 10, 6, tzinfo=timezone.utc),
        ],
    })

    gaps = validation_service.detect_missing_gaps(df, timeframe="1m", is_crypto=True)
    assert len(gaps) == 1
    assert gaps[0]["missing_duration_seconds"] == 300.0

