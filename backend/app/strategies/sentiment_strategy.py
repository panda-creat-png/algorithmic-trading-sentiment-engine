from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import polars as pl
from app.strategies.base import BaseStrategy


class AISentimentStrategy(BaseStrategy):
    """
    FinBERT AI Sentiment-Driven Trading Strategy.
    
    CRITICAL LOOK-AHEAD BIAS PREVENTION:
    Signals for candle t are generated ONLY using news published strictly ON OR BEFORE candle t's timestamp.
    Under no circumstances is any news published after candle t's timestamp allowed into the calculation.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="AI Sentiment-Based Strategy",
            strategy_type="sentiment",
            parameters=parameters or {}
        )
        self.sentiment_threshold = float(self.get_parameter("sentiment_threshold", 0.65))
        self.min_confidence = float(self.get_parameter("min_confidence", 0.70))

    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        if df.is_empty():
            return df.with_columns(pl.lit(0).alias("signal"))

        if not news_sentiment:
            # If no sentiment feed provided, fallback to neutral
            return df.with_columns(pl.lit(0).alias("signal"))

        # Sort news by published_at
        sorted_news = []
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

        signals = []
        timestamps = df["timestamp"].to_list()
        
        # Chronological iteration: for each candle, look at news published <= candle timestamp
        news_idx = 0
        latest_sentiment_score = 0.0  # -1.0 to +1.0 net
        latest_confidence = 0.0

        for i, candle_ts in enumerate(timestamps):
            if hasattr(candle_ts, "tzinfo") and candle_ts.tzinfo is None:
                candle_ts = candle_ts.replace(tzinfo=timezone.utc)

            # Ingest all news published up to this candle's close
            while news_idx < len(sorted_news) and sorted_news[news_idx][0] <= candle_ts:
                item = sorted_news[news_idx][1]
                pos = float(item.get("positive_score", 0.0))
                neg = float(item.get("negative_score", 0.0))
                conf = float(item.get("confidence", 0.0))
                latest_sentiment_score = pos - neg
                latest_confidence = conf
                news_idx += 1

            # Emit signal based only on already published news
            sig = 0
            if latest_confidence >= self.min_confidence:
                if latest_sentiment_score >= (self.sentiment_threshold - 0.5):
                    sig = 1
                elif latest_sentiment_score <= -(self.sentiment_threshold - 0.5):
                    sig = -1

            signals.append(sig)

        return df.with_columns(pl.Series("signal", signals, dtype=pl.Int32))
