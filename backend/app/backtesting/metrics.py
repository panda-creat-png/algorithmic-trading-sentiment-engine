import math
from typing import List, Dict, Any, Optional
import numpy as np


class PerformanceMetricsCalculator:
    """
    Institutional Quantitative Performance Analytics Engine.
    Calculates risk-adjusted returns, drawdown dynamics, and trade distribution metrics.
    """

    @staticmethod
    def calculate(
        initial_capital: float,
        final_equity: float,
        equity_curve: List[Dict[str, Any]],
        trades: List[Dict[str, Any]],
        benchmark_initial_price: Optional[float] = None,
        benchmark_final_price: Optional[float] = None,
        risk_free_rate: float = 0.04,  # 4% annual risk-free rate
        trading_days_per_year: int = 252
    ) -> Dict[str, Any]:
        """
        Computes all standard institutional quantitative metrics.
        """
        # 1. Total Return
        total_return = (final_equity - initial_capital) / initial_capital if initial_capital > 0 else 0.0

        # Extract daily returns from equity curve
        if len(equity_curve) > 1:
            equities = np.array([point["equity"] for point in equity_curve], dtype=np.float64)
            # Candle returns: r_t = (E_t - E_{t-1}) / E_{t-1}
            returns = np.diff(equities) / equities[:-1]
            returns = np.nan_to_num(returns, nan=0.0, posinf=0.0, neginf=0.0)
        else:
            equities = np.array([initial_capital, final_equity], dtype=np.float64)
            returns = np.array([0.0], dtype=np.float64)

        # Total duration in days
        total_points = len(equity_curve)
        if total_points > 1 and "timestamp" in equity_curve[0] and "timestamp" in equity_curve[-1]:
            t_start = equity_curve[0]["timestamp"]
            t_end = equity_curve[-1]["timestamp"]
            if hasattr(t_start, "timestamp") and hasattr(t_end, "timestamp"):
                duration_days = max(1.0, (t_end.timestamp() - t_start.timestamp()) / 86400.0)
            else:
                duration_days = max(1.0, float(total_points))
        else:
            duration_days = max(1.0, float(total_points))

        # 2. CAGR (Compound Annual Growth Rate)
        years = duration_days / 365.25
        if years > 0 and final_equity > 0 and initial_capital > 0:
            cagr = (final_equity / initial_capital) ** (1.0 / years) - 1.0
        else:
            cagr = 0.0

        # 3. Annualized Volatility
        daily_std = float(np.std(returns)) if len(returns) > 1 else 0.0
        annualized_volatility = daily_std * math.sqrt(trading_days_per_year)

        # 4. Sharpe Ratio
        mean_return = float(np.mean(returns)) if len(returns) > 0 else 0.0
        daily_rf = (1.0 + risk_free_rate) ** (1.0 / trading_days_per_year) - 1.0
        excess_mean = mean_return - daily_rf
        if daily_std > 1e-8:
            sharpe_ratio = (excess_mean / daily_std) * math.sqrt(trading_days_per_year)
        else:
            sharpe_ratio = 0.0

        # 5. Sortino Ratio (Downside deviation only)
        downside_returns = returns[returns < daily_rf]
        if len(downside_returns) > 0:
            downside_std = float(np.sqrt(np.mean((downside_returns - daily_rf) ** 2)))
            sortino_ratio = (excess_mean / downside_std) * math.sqrt(trading_days_per_year) if downside_std > 1e-8 else 0.0
        else:
            sortino_ratio = sharpe_ratio if sharpe_ratio > 0 else 0.0

        # 6. Maximum Drawdown (MDD)
        peak = equities[0]
        max_drawdown = 0.0
        for eq in equities:
            if eq > peak:
                peak = eq
            dd = (eq - peak) / peak if peak > 0 else 0.0
            if dd < max_drawdown:
                max_drawdown = dd

        # 7. Calmar Ratio
        abs_mdd = abs(max_drawdown)
        if abs_mdd > 1e-6:
            calmar_ratio = cagr / abs_mdd
        else:
            calmar_ratio = 0.0

        # 8. Trade Statistics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.get("realized_pnl", 0.0) > 0]
        losing_trades = [t for t in trades if t.get("realized_pnl", 0.0) < 0]
        
        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        win_rate = num_wins / total_trades if total_trades > 0 else 0.0

        gross_profit = sum(t.get("realized_pnl", 0.0) for t in winning_trades)
        gross_loss = abs(sum(t.get("realized_pnl", 0.0) for t in losing_trades))

        if gross_loss > 1e-6:
            profit_factor = gross_profit / gross_loss
        elif gross_profit > 0:
            profit_factor = 99.0  # Infinite / maximum display value
        else:
            profit_factor = 0.0

        avg_winning_trade = gross_profit / num_wins if num_wins > 0 else 0.0
        avg_losing_trade = -gross_loss / num_losses if num_losses > 0 else 0.0

        # 9. Exposure Time (% of time invested)
        invested_candles = sum(1 for pt in equity_curve if pt.get("position_size", 0.0) > 0)
        exposure_time = invested_candles / total_points if total_points > 0 else 0.0

        # 10. Benchmark Comparison (Buy & Hold)
        if benchmark_initial_price and benchmark_final_price and benchmark_initial_price > 0:
            benchmark_return = (benchmark_final_price - benchmark_initial_price) / benchmark_initial_price
        else:
            benchmark_return = None

        return {
            "total_return": round(float(total_return), 4),
            "cagr": round(float(cagr), 4),
            "sharpe_ratio": round(float(sharpe_ratio), 2),
            "sortino_ratio": round(float(sortino_ratio), 2),
            "max_drawdown": round(float(max_drawdown), 4),
            "calmar_ratio": round(float(calmar_ratio), 2),
            "win_rate": round(float(win_rate), 4),
            "profit_factor": round(float(profit_factor), 2),
            "avg_winning_trade": round(float(avg_winning_trade), 2),
            "avg_losing_trade": round(float(avg_losing_trade), 2),
            "total_trades": total_trades,
            "annualized_volatility": round(float(annualized_volatility), 4),
            "exposure_time": round(float(exposure_time), 4),
            "benchmark_return": round(float(benchmark_return), 4) if benchmark_return is not None else None,
        }
