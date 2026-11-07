from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy
from app.indicators.technical_engine import technical_engine


class MACDStrategy(BaseStrategy):
    """
    MACD Crossover Strategy.
    
    Logic:
    - Long Signal (1): MACD line crosses ABOVE Signal line.
    - Exit / Short Signal (-1): MACD line crosses BELOW Signal line.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="MACD Crossover",
            strategy_type="macd",
            parameters=parameters or {}
        )
        self.fast = int(self.get_parameter("fast", 12))
        self.slow = int(self.get_parameter("slow", 26))
        self.signal = int(self.get_parameter("signal", 9))

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.height < self.slow + self.signal + 2:
            return df.with_columns(pl.lit(0).alias("signal"))

        macd_dict = technical_engine.calc_macd(df, fast=self.fast, slow=self.slow, signal_period=self.signal)
        result = df.with_columns([
            macd_dict["macd_line"].alias("macd"),
            macd_dict["signal_line"].alias("macd_signal"),
            macd_dict["histogram"].alias("macd_hist")
        ])

        result = result.with_columns([
            pl.col("macd").shift(1).alias("prev_macd"),
            pl.col("macd_signal").shift(1).alias("prev_signal")
        ])

        result = result.with_columns(
            pl.when(
                (pl.col("prev_macd") <= pl.col("prev_signal")) &
                (pl.col("macd") > pl.col("macd_signal"))
            )
            .then(pl.lit(1))
            .when(
                (pl.col("prev_macd") >= pl.col("prev_signal")) &
                (pl.col("macd") < pl.col("macd_signal"))
            )
            .then(pl.lit(-1))
            .otherwise(pl.lit(0))
            .alias("signal")
        ).drop(["prev_macd", "prev_signal"])

        return result
