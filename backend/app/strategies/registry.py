from typing import Dict, Any, Type
from app.strategies.base import BaseStrategy
from app.strategies.ma_crossover import MovingAverageCrossoverStrategy
from app.strategies.rsi_reversal import RSIStrategy
from app.strategies.macd_crossover import MACDStrategy
from app.strategies.bollinger_reversal import BollingerBandsStrategy
from app.strategies.momentum import MomentumStrategy
from app.strategies.sentiment_strategy import AISentimentStrategy
from app.strategies.combined_strategy import CombinedTechnicalSentimentStrategy


STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "ma_crossover": MovingAverageCrossoverStrategy,
    "rsi_reversal": RSIStrategy,
    "macd": MACDStrategy,
    "bollinger": BollingerBandsStrategy,
    "momentum": MomentumStrategy,
    "sentiment": AISentimentStrategy,
    "combined": CombinedTechnicalSentimentStrategy,
}


def get_strategy(strategy_type: str, parameters: Dict[str, Any] = None) -> BaseStrategy:
    """
    Factory function to instantiate a strategy by its type key.
    
    Raises:
        ValueError if strategy_type is not registered.
    """
    cls = STRATEGY_REGISTRY.get(strategy_type.lower())
    if not cls:
        valid_types = ", ".join(STRATEGY_REGISTRY.keys())
        raise ValueError(f"Unknown strategy_type '{strategy_type}'. Valid types: {valid_types}")
    return cls(parameters=parameters or {})
