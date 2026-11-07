from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy
from app.indicators.technical_engine import technical_engine


class RSIStrategy(BaseStrategy):
    """
    RSI Mean Reversion Strategy.
    
    Logic:
    - Long Signal (1): RSI rebounds and crosses ABOVE oversold threshold (default 30).
    - Exit / Short Signal (-1): RSI drops and crosses BELOW overbought threshold (default 70).
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="RSI Mean Reversion",
            strategy_type="rsi_reversal",
            parameters=parameters or {}
        )
        self.period = int(self.get_parameter("rsi_period", 14))
        self.oversold = float(self.get_parameter("oversold", 30.0))
        self.overbought = float(self.get_parameter("overbought", 70.0))

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.height < self.period + 5:
            return df.with_columns(pl.lit(0).alias("signal"))

        # Compute RSI using technical_engine
        rsi_series = technical_engine.calc_rsi(df, period=self.period).alias(f"rsi_{self.period}")
        result = df.with_columns(rsi_series)

        result = result.with_columns(
            pl.col(f"rsi_{self.period}").shift(1).alias("prev_rsi")
        )

        result = result.with_columns(
            pl.when(
                (pl.col("prev_rsi") <= self.oversold) &
                (pl.col(f"rsi_{self.period}") > self.oversold)
            )
            .then(pl.lit(1))
            .when(
                (pl.col("prev_rsi") >= self.overbought) &
                (pl.col(f"rsi_{self.period}") < self.overbought)
            )
            .then(pl.lit(-1))
            .otherwise(pl.lit(0))
            .alias("signal")
        ).drop(["prev_rsi"])

        return result
