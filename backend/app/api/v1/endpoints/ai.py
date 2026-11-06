from typing import List
from fastapi import APIRouter
from app.schemas.ai import SentimentAnalyzeRequest, SentimentResult, MarketSentimentOverview

router = APIRouter()


@router.post("/analyze", response_model=SentimentResult, summary="Analyze Financial Headline Sentiment")
async def analyze_sentiment(payload: SentimentAnalyzeRequest):
    """Executes AI sentiment classification on input text."""
    # Structural Phase 1 fallback / rule-based response before FinBERT deep integration in Phase 3
    lowered = payload.text.lower()
    pos_words = ["surge", "beat", "record", "profit", "gain", "bullish", "high", "growth", "strong"]
    neg_words = ["drop", "miss", "loss", "plunge", "bearish", "fall", "decline", "weak", "warning"]
    
    pos_matches = sum(1 for w in pos_words if w in lowered)
    neg_matches = sum(1 for w in neg_words if w in lowered)
    
    if pos_matches > neg_matches:
        sentiment = "positive"
        pos, neg, neu = 0.88, 0.05, 0.07
    elif neg_matches > pos_matches:
        sentiment = "negative"
        pos, neg, neu = 0.05, 0.88, 0.07
    else:
        sentiment = "neutral"
        pos, neg, neu = 0.15, 0.15, 0.70

    return SentimentResult(
        headline=payload.text,
        symbol=payload.symbol,
        sentiment=sentiment,
        positive_score=pos,
        negative_score=neg,
        neutral_score=neu,
        confidence=max(pos, neg, neu),
        relevance_score=0.95,
        model_name="ProsusAI/finbert (Phase 1 Stub)"
    )


@router.get("/sentiment/{symbol}", response_model=MarketSentimentOverview, summary="Get Asset Sentiment Metrics")
async def get_asset_sentiment(symbol: str):
    """Returns aggregated sentiment metrics for a specific symbol."""
    return MarketSentimentOverview(
        bullish_index=0.62,
        bearish_index=0.18,
        neutral_index=0.20,
        overall_sentiment="bullish",
        sentiment_trend="positive",
        analyzed_headlines_count=12
    )

