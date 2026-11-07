from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy
from app.indicators.technical_engine import technical_engine


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Dual Moving Average Crossover Strategy (Golden Cross / Death Cross).
    
    Logic:
    - Long Signal (1): Fast SMA crosses ABOVE Slow SMA.
    - Exit / Short Signal (-1): Fast SMA crosses BELOW Slow SMA.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Dual Moving Average Crossover",
            strategy_type="ma_crossover",
            parameters=parameters or {}
        )
        self.fast_period = int(self.get_parameter("fast_period", 20))
        self.slow_period = int(self.get_parameter("slow_period", 50))

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.height < self.slow_period + 2:
            return df.with_columns(pl.lit(0).alias("signal"))

        # Calculate SMAs using Polars vectorized expressions
        result = df.with_columns([
            pl.col("close").rolling_mean(window_size=self.fast_period).alias("sma_fast"),
            pl.col("close").rolling_mean(window_size=self.slow_period).alias("sma_slow"),
        ])

        # Detect crossover:
        # Cross above: prev(fast <= slow) and curr(fast > slow)
        # Cross below: prev(fast >= slow) and curr(fast < slow)
        result = result.with_columns([
            pl.col("sma_fast").shift(1).alias("prev_fast"),
            pl.col("sma_slow").shift(1).alias("prev_slow"),
        ])

        result = result.with_columns(
            pl.when(
                (pl.col("prev_fast") <= pl.col("prev_slow")) &
                (pl.col("sma_fast") > pl.col("sma_slow"))
            )
            .then(pl.lit(1))
            .when(
                (pl.col("prev_fast") >= pl.col("prev_slow")) &
                (pl.col("sma_fast") < pl.col("sma_slow"))
            )
            .then(pl.lit(-1))
            .otherwise(pl.lit(0))
            .alias("signal")
        ).drop(["prev_fast", "prev_slow"])

        return result

