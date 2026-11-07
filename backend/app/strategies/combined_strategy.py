from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy
from app.indicators.technical_engine import technical_engine


class CombinedTechnicalSentimentStrategy(BaseStrategy):
    """
    Combined Technical Analysis + AI FinBERT Sentiment Multi-Factor Strategy.
    
    Filters technical momentum (RSI) using institutional AI sentiment confirmation.
    - Long (1): RSI > rsi_threshold (e.g. 50) AND latest FinBERT net sentiment is Bullish.
    - Exit / Short (-1): RSI < rsi_threshold AND latest FinBERT net sentiment is Bearish.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Combined Technical + Sentiment Strategy",
            strategy_type="combined",
            parameters=parameters or {}
        )
        self.rsi_period = int(self.get_parameter("rsi_period", 14))
        self.rsi_threshold = float(self.get_parameter("rsi_threshold", 50.0))
        self.sentiment_threshold = float(self.get_parameter("sentiment_threshold", 0.60))

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.height < self.rsi_period + 2:
            return df.with_columns(pl.lit(0).alias("signal"))

        # 1. Compute RSI
        rsi_series = technical_engine.calc_rsi(df, period=self.rsi_period).alias(f"rsi_{self.rsi_period}")
        result = df.with_columns(rsi_series)

        # 2. Process news strictly chronologically
        sorted_news = []
        if news_sentiment:
            for item in news_sentiment:
                pub_time = item.get("published_at")
                if isinstance(pub_time, str):
                    try:
                        pub_time = datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
                    except Exception:
                        continue
                if pub_time:
                    if pub_time.tzinfo is None:
                        pub_time = pub_time.replace(tzinfo=timezone.utc)
                    sorted_news.append((pub_time, item))
            sorted_news.sort(key=lambda x: x[0])

        timestamps = result["timestamp"].to_list()
        rsi_vals = result[f"rsi_{self.rsi_period}"].to_list()
        signals = []
        
        news_idx = 0
        latest_net_sentiment = 0.0

        for i, candle_ts in enumerate(timestamps):
            if hasattr(candle_ts, "tzinfo") and candle_ts.tzinfo is None:
                candle_ts = candle_ts.replace(tzinfo=timezone.utc)

            # Ingest only news published up to this candle
            while news_idx < len(sorted_news) and sorted_news[news_idx][0] <= candle_ts:
                item = sorted_news[news_idx][1]
                pos = float(item.get("positive_score", 0.0))
                neg = float(item.get("negative_score", 0.0))
                latest_net_sentiment = pos - neg
                news_idx += 1

            rsi_val = rsi_vals[i]
            sig = 0
            if rsi_val is not None:
                # Bullish confluence
                if rsi_val >= self.rsi_threshold and latest_net_sentiment >= (self.sentiment_threshold - 0.5):
                    sig = 1
                # Bearish confluence
                elif rsi_val < self.rsi_threshold and latest_net_sentiment <= -(self.sentiment_threshold - 0.5):
                    sig = -1

            signals.append(sig)

        return result.with_columns(pl.Series("signal", signals, dtype=pl.Int32))
