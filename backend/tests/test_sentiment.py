import pytest
from httpx import AsyncClient
from app.sentiment.finbert_engine import finbert_engine


def test_finbert_positive_sentiment_inference():
    headline = "NVIDIA reports record quarterly revenue and surges in AI datacenter demand"
    res = finbert_engine.analyze_headline(headline, symbol="NVDA")
    assert res["sentiment"] == "positive"
    assert res["positive_score"] > 0.60
    assert res["confidence"] > 0.60
    assert res["symbol"] == "NVDA"
    assert res["relevance_score"] >= 0.90


def test_finbert_negative_sentiment_inference():
    headline = "Company profits plunge amid regulatory investigation and warning of lower guidance"
    res = finbert_engine.analyze_headline(headline)
    assert res["sentiment"] == "negative"
    assert res["negative_score"] > 0.60
    assert res["confidence"] > 0.60


def test_entity_extraction_and_relevance():
    headline = "Apple releases new AI chips and iPhones during Cupertino launch event"
    info = finbert_engine.extract_entities_and_relevance(headline, target_symbol="AAPL")
    assert "AAPL" in info["matched_symbols"]
    assert info["relevance_score"] >= 0.90


def test_sentiment_aggregation_metrics():
    sample_records = [
        {"positive_score": 0.85, "negative_score": 0.05, "neutral_score": 0.10},
        {"positive_score": 0.90, "negative_score": 0.02, "neutral_score": 0.08},
        {"positive_score": 0.70, "negative_score": 0.10, "neutral_score": 0.20},
    ]
    metrics = finbert_engine.aggregate_sentiment_metrics(sample_records)
    assert metrics["bullish_index"] > 0.75
    assert metrics["overall_sentiment"] == "bullish"
    assert metrics["sentiment_trend"] == "improving"
    assert metrics["analyzed_headlines_count"] == 3


@pytest.mark.asyncio
async def test_ai_analyze_api_endpoint(async_client: AsyncClient):
    payload = {
        "text": "Microsoft cloud growth exceeds estimates with surging Azure AI revenue",
        "symbol": "MSFT",
    }
    response = await async_client.post("/api/v1/ai/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert data["positive_score"] > 0.60
    assert data["symbol"] == "MSFT"


@pytest.mark.asyncio
async def test_ai_correlation_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ai/correlation/NVDA?timeframe=1d")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "NVDA"
    assert "time_windows" in data
    assert "1h" in data["time_windows"]
    assert "24h" in data["time_windows"]

