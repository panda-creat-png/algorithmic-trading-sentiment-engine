from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Momentum / Rate of Change (ROC) Strategy.
    
    Logic:
    - ROC = (Close_t - Close_{t-n}) / Close_{t-n}
    - Long Signal (1): ROC crosses ABOVE positive threshold.
    - Exit / Short Signal (-1): ROC crosses BELOW negative threshold or 0.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Momentum Breakout",
            strategy_type="momentum",
            parameters=parameters or {}
        )
        self.lookback = int(self.get_parameter("lookback", 14))
        self.threshold = float(self.get_parameter("threshold", 0.02))  # 2% breakout

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.height < self.lookback + 2:
            return df.with_columns(pl.lit(0).alias("signal"))

        # Compute ROC
        result = df.with_columns([
            ((pl.col("close") - pl.col("close").shift(self.lookback)) / pl.col("close").shift(self.lookback)).alias("roc")
        ])

        result = result.with_columns(
            pl.col("roc").shift(1).alias("prev_roc")
        )

        result = result.with_columns(
            pl.when(
                (pl.col("prev_roc") <= self.threshold) &
                (pl.col("roc") > self.threshold)
            )
            .then(pl.lit(1))
            .when(
                (pl.col("prev_roc") >= -self.threshold) &
                (pl.col("roc") < -self.threshold)
            )
            .then(pl.lit(-1))
            .otherwise(pl.lit(0))
            .alias("signal")
        ).drop(["prev_roc"])

        return result

