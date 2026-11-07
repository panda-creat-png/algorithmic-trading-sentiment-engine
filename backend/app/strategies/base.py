from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import polars as pl


class BaseStrategy(ABC):
    """
    Abstract Base Class for all quantitative trading strategies.
    Enforces strict modularity and zero look-ahead bias.
    """

    def __init__(self, name: str, strategy_type: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.strategy_type = strategy_type
        self.parameters = parameters or {}

    @abstractmethod
    def generate_signals(
        self,
        df: pl.DataFrame,
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> pl.DataFrame:
        """
        Generates trading signals for each candle in the historical DataFrame.
        
        CRITICAL ZERO LOOK-AHEAD REQUIREMENT:
        Signal generated on row i MUST only use data available up to row i (Close, High, Low, Open, Volume).
        The signal produced here (+1 for LONG ENTRY, -1 for SHORT ENTRY / EXIT, 0 for HOLD)
        will be executed by the backtest engine on row i+1 at Open price.
        
        Args:
            df: Historical OHLCV Polars DataFrame sorted chronologically.
            news_sentiment: Optional chronological list of news items with timestamps and FinBERT sentiment.
            
        Returns:
            pl.DataFrame: Input DataFrame augmented with:
                - 'signal': int (1 = Long entry, -1 = Short entry or Long exit, 0 = Hold)
                - Strategy-specific indicator columns (e.g. 'sma_fast', 'rsi', etc.)
        """
        pass

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Retrieves a parameter value with an optional default fallback."""
        return self.parameters.get(key, default)
