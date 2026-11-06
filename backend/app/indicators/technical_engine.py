import numpy as np
import polars as pl
from typing import Dict, Any, List, Optional
from app.core.logging import logger


class TechnicalAnalysisEngine:
    """High-performance vectorized technical analysis engine powered by Polars."""

    @staticmethod
    def calc_sma(df: pl.DataFrame, col: str = "close", window: int = 20) -> pl.Series:
        """Calculates Simple Moving Average (SMA)."""
        return df[col].rolling_mean(window_size=window)

    @staticmethod
    def calc_ema(df: pl.DataFrame, col: str = "close", span: int = 20) -> pl.Series:
        """Calculates Exponential Moving Average (EMA)."""
        # Polars native ewm_mean
        return df[col].ewm_mean(span=span)

    @staticmethod
    def calc_rsi(df: pl.DataFrame, col: str = "close", period: int = 14) -> pl.Series:
        """Calculates Relative Strength Index (RSI)."""
        if len(df) < period + 1:
            return pl.Series("rsi", [50.0] * len(df))

        delta = df[col].diff()
        gain = pl.when(delta > 0).then(delta).otherwise(0.0)
        loss = pl.when(delta < 0).then(-delta).otherwise(0.0)

        # Exponential moving average of gains and losses (Wilder smoothing)
        avg_gain = gain.ewm_mean(alpha=1.0 / period)
        avg_loss = loss.ewm_mean(alpha=1.0 / period)

        rs = avg_gain / pl.when(avg_loss == 0).then(1e-10).otherwise(avg_loss)
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Fill leading nulls with 50.0 (neutral)
        return rsi.fill_null(50.0)

    @staticmethod
    def calc_macd(
        df: pl.DataFrame, col: str = "close", fast: int = 12, slow: int = 26, signal_period: int = 9
    ) -> Dict[str, pl.Series]:
        """Calculates Moving Average Convergence Divergence (MACD), Signal Line, and Histogram."""
        ema_fast = df[col].ewm_mean(span=fast)
        ema_slow = df[col].ewm_mean(span=slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm_mean(span=signal_period)
        histogram = macd_line - signal_line

        return {
            "macd_line": macd_line.fill_null(0.0),
            "signal_line": signal_line.fill_null(0.0),
            "histogram": histogram.fill_null(0.0),
        }

    @staticmethod
    def calc_bollinger_bands(
        df: pl.DataFrame, col: str = "close", period: int = 20, num_std: float = 2.0
    ) -> Dict[str, pl.Series]:
        """Calculates Bollinger Bands: Middle, Upper, Lower, %B, and Bandwidth."""
        middle = df[col].rolling_mean(window_size=period)
        std = df[col].rolling_std(window_size=period)

        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        bandwidth = (upper - lower) / pl.when(middle == 0).then(1e-10).otherwise(middle)
        pct_b = (df[col] - lower) / pl.when(upper - lower == 0).then(1e-10).otherwise(upper - lower)

        return {
            "bb_middle": middle.fill_null(df[col]),
            "bb_upper": upper.fill_null(df[col]),
            "bb_lower": lower.fill_null(df[col]),
            "bb_bandwidth": bandwidth.fill_null(0.0),
            "bb_pct_b": pct_b.fill_null(0.5),
        }

    @staticmethod
    def calc_atr(df: pl.DataFrame, period: int = 14) -> pl.Series:
        """Calculates Average True Range (ATR)."""
        if len(df) < 2:
            return pl.Series("atr", [0.0] * len(df))

        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1).fill_null(close)

        # TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()

        # Combine into True Range
        tr = pl.max_horizontal(tr1, tr2, tr3)
        atr = tr.ewm_mean(alpha=1.0 / period).fill_null(tr)
        return atr

    @staticmethod
    def calc_stochastic(
        df: pl.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> Dict[str, pl.Series]:
        """Calculates Stochastic Oscillator (%K and %D)."""
        lowest_low = df["low"].rolling_min(window_size=k_period)
        highest_high = df["high"].rolling_max(window_size=k_period)

        range_hl = highest_high - lowest_low
        k_percent = 100.0 * (df["close"] - lowest_low) / pl.when(range_hl == 0).then(1e-10).otherwise(range_hl)
        d_percent = k_percent.rolling_mean(window_size=d_period)

        return {
            "stoch_k": k_percent.fill_null(50.0),
            "stoch_d": d_percent.fill_null(50.0),
        }

    @classmethod
    def compute_all_indicators(cls, df: pl.DataFrame) -> pl.DataFrame:
        """Computes complete standard institutional technical indicators suite on OHLCV DataFrame."""
        if df.is_empty():
            return df

        # SMAs
        sma_20 = cls.calc_sma(df, "close", 20).alias("sma_20")
        sma_50 = cls.calc_sma(df, "close", 50).alias("sma_50")
        sma_200 = cls.calc_sma(df, "close", 200).alias("sma_200")

        # EMAs
        ema_12 = cls.calc_ema(df, "close", 12).alias("ema_12")
        ema_26 = cls.calc_ema(df, "close", 26).alias("ema_26")

        # RSI
        rsi_14 = cls.calc_rsi(df, "close", 14).alias("rsi_14")

        # MACD
        macd_dict = cls.calc_macd(df, "close", 12, 26, 9)
        macd_line = macd_dict["macd_line"].alias("macd_line")
        macd_signal = macd_dict["signal_line"].alias("macd_signal")
        macd_hist = macd_dict["histogram"].alias("macd_hist")

        # Bollinger Bands
        bb_dict = cls.calc_bollinger_bands(df, "close", 20, 2.0)
        bb_upper = bb_dict["bb_upper"].alias("bb_upper")
        bb_middle = bb_dict["bb_middle"].alias("bb_middle")
        bb_lower = bb_dict["bb_lower"].alias("bb_lower")
        bb_pct_b = bb_dict["bb_pct_b"].alias("bb_pct_b")

        # ATR
        atr_14 = cls.calc_atr(df, 14).alias("atr_14")

        # Stochastic
        stoch_dict = cls.calc_stochastic(df, 14, 3)
        stoch_k = stoch_dict["stoch_k"].alias("stoch_k")
        stoch_d = stoch_dict["stoch_d"].alias("stoch_d")

        # Volume MA
        vol_ma_20 = df["volume"].rolling_mean(window_size=20).alias("vol_ma_20")

        return df.with_columns([
            sma_20,
            sma_50,
            sma_200,
            ema_12,
            ema_26,
            rsi_14,
            macd_line,
            macd_signal,
            macd_hist,
            bb_upper,
            bb_middle,
            bb_lower,
            bb_pct_b,
            atr_14,
            stoch_k,
            stoch_d,
            vol_ma_20,
        ])

    @classmethod
    def generate_signals(cls, df: pl.DataFrame) -> Dict[str, Any]:
        """Generates quantitative signals from technical indicator values at current (latest) bar."""
        if len(df) < 2:
            return {"status": "insufficient_data", "signals": []}

        df_ind = cls.compute_all_indicators(df)
        curr = df_ind.tail(1).to_dicts()[0]
        prev = df_ind.tail(2).head(1).to_dicts()[0]

        signals = []

        # 1. Moving Average Crossovers
        if curr.get("sma_20") and curr.get("sma_50") and prev.get("sma_20") and prev.get("sma_50"):
            if prev["sma_20"] <= prev["sma_50"] and curr["sma_20"] > curr["sma_50"]:
                signals.append({"type": "GOLDEN_CROSS", "indicator": "SMA_20_50", "signal": "BULLISH", "strength": 0.85})
            elif prev["sma_20"] >= prev["sma_50"] and curr["sma_20"] < curr["sma_50"]:
                signals.append({"type": "DEATH_CROSS", "indicator": "SMA_20_50", "signal": "BEARISH", "strength": 0.85})

        # 2. RSI Overbought / Oversold
        rsi = curr.get("rsi_14", 50.0)
        if rsi < 30.0:
            signals.append({"type": "RSI_OVERSOLD", "indicator": "RSI_14", "signal": "BULLISH", "value": round(rsi, 2), "strength": 0.75})
        elif rsi > 70.0:
            signals.append({"type": "RSI_OVERBOUGHT", "indicator": "RSI_14", "signal": "BEARISH", "value": round(rsi, 2), "strength": 0.75})

        # 3. MACD Crossover
        if curr.get("macd_line") is not None and curr.get("macd_signal") is not None:
            if prev.get("macd_line", 0) <= prev.get("macd_signal", 0) and curr["macd_line"] > curr["macd_signal"]:
                signals.append({"type": "MACD_BULLISH_CROSS", "indicator": "MACD", "signal": "BULLISH", "strength": 0.80})
            elif prev.get("macd_line", 0) >= prev.get("macd_signal", 0) and curr["macd_line"] < curr["macd_signal"]:
                signals.append({"type": "MACD_BEARISH_CROSS", "indicator": "MACD", "signal": "BEARISH", "strength": 0.80})

        # 4. Bollinger Band Breakout
        close = curr["close"]
        bb_upper = curr.get("bb_upper", close * 2)
        bb_lower = curr.get("bb_lower", 0)
        if close > bb_upper:
            signals.append({"type": "BB_UPPER_BREAKOUT", "indicator": "BOLLINGER", "signal": "BULLISH_MOMENTUM", "strength": 0.70})
        elif close < bb_lower:
            signals.append({"type": "BB_LOWER_BREAKOUT", "indicator": "BOLLINGER", "signal": "BEARISH_OVERSOLD", "strength": 0.70})

        # Calculate overall technical score (-1.0 to +1.0)
        bullish_weights = [s["strength"] for s in signals if "BULLISH" in s["signal"]]
        bearish_weights = [s["strength"] for s in signals if "BEARISH" in s["signal"]]

        bullish_sum = sum(bullish_weights)
        bearish_sum = sum(bearish_weights)
        net_score = (bullish_sum - bearish_sum) / (max(len(signals), 1))

        sentiment_label = "BULLISH" if net_score > 0.15 else "BEARISH" if net_score < -0.15 else "NEUTRAL"

        return {
            "status": "computed",
            "net_score": round(net_score, 2),
            "bias": sentiment_label,
            "signals": signals,
            "latest_metrics": {
                "close": curr["close"],
                "rsi_14": round(curr.get("rsi_14", 50.0), 2),
                "sma_20": round(curr.get("sma_20", 0.0), 2) if curr.get("sma_20") else None,
                "sma_50": round(curr.get("sma_50", 0.0), 2) if curr.get("sma_50") else None,
                "macd_line": round(curr.get("macd_line", 0.0), 2) if curr.get("macd_line") else None,
                "macd_signal": round(curr.get("macd_signal", 0.0), 2) if curr.get("macd_signal") else None,
                "bb_upper": round(curr.get("bb_upper", 0.0), 2) if curr.get("bb_upper") else None,
                "bb_lower": round(curr.get("bb_lower", 0.0), 2) if curr.get("bb_lower") else None,
                "atr_14": round(curr.get("atr_14", 0.0), 2) if curr.get("atr_14") else None,
                "vol_ma_20": round(curr.get("vol_ma_20", 0.0), 2) if curr.get("vol_ma_20") else None,
            }
        }


technical_engine = TechnicalAnalysisEngine()
