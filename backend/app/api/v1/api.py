from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    market,
    news,
    ai,
    strategies,
    backtests,
    portfolio,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(news.router, prefix="/news", tags=["Financial News"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI & Sentiment"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Trading Strategies"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["Backtesting Engine"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio Simulator"])

