from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy
from app.indicators.technical_engine import technical_engine


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Mean Reversion Strategy.
    
    Logic:
    - Long Signal (1): Close dips below or touches Lower Band and bounces back up.
    - Exit / Short Signal (-1): Close reaches or exceeds Upper Band.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Bollinger Bands Reversal",
            strategy_type="bollinger",
            parameters=parameters or {}
        )
        self.period = int(self.get_parameter("period", 20))
        self.num_std = float(self.get_parameter("std_dev", 2.0))

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.height < self.period + 2:
            return df.with_columns(pl.lit(0).alias("signal"))

        bb_dict = technical_engine.calc_bollinger_bands(df, period=self.period, num_std=self.num_std)
        result = df.with_columns([
            bb_dict["bb_upper"],
            bb_dict["bb_middle"],
            bb_dict["bb_lower"]
        ])

        result = result.with_columns([
            pl.col("close").shift(1).alias("prev_close"),
            pl.col("bb_lower").shift(1).alias("prev_bb_lower"),
            pl.col("bb_upper").shift(1).alias("prev_bb_upper")
        ])

        result = result.with_columns(
            pl.when(
                (pl.col("prev_close") <= pl.col("prev_bb_lower")) &
                (pl.col("close") > pl.col("bb_lower"))
            )
            .then(pl.lit(1))
            .when(
                (pl.col("close") >= pl.col("bb_upper"))
            )
            .then(pl.lit(-1))
            .otherwise(pl.lit(0))
            .alias("signal")
        ).drop(["prev_close", "prev_bb_lower", "prev_bb_upper"])

        return result
