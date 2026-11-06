from typing import Optional, List
from pydantic import BaseModel, Field


class SentimentAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=3, description="Financial news headline or snippet to analyze")
    symbol: Optional[str] = Field(None, description="Optional associated ticker symbol (e.g. AAPL, NVDA)")


class SentimentResult(BaseModel):
    headline: str
    symbol: Optional[str] = None
    sentiment: str = Field(..., description="positive | negative | neutral")
    positive_score: float = Field(..., ge=0.0, le=1.0)
    negative_score: float = Field(..., ge=0.0, le=1.0)
    neutral_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    model_name: str = "ProsusAI/finbert"


class SentimentBatchRequest(BaseModel):
    items: List[SentimentAnalyzeRequest]


class SentimentBatchResponse(BaseModel):
    total_processed: int
    results: List[SentimentResult]


class MarketSentimentOverview(BaseModel):
    bullish_index: float
    bearish_index: float
    neutral_index: float
    overall_sentiment: str
    sentiment_trend: str
    analyzed_headlines_count: int

