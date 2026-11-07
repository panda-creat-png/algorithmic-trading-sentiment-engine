from datetime import datetime
from typing import Dict, Any, List, Optional
import polars as pl
from app.strategies.base import BaseStrategy
from app.backtesting.metrics import PerformanceMetricsCalculator


class BacktestEngine:
    """
    Institutional Event-Driven Backtesting Engine.
    
    GUARANTEES:
    1. ZERO LOOK-AHEAD BIAS:
       - Strategy produces a signal on candle t using only information up to candle t Close.
       - The order is queued and EXECUTED at candle t+1 OPEN price.
       - No future information is ever leaked into the decision boundary.
    2. REALISTIC SLIPPAGE & FEES:
       - Executions incur proportional fee rate and price impact slippage.
    3. INTRADAY RISK CONTROLS:
       - Checks Stop-Loss and Take-Profit limits against candle High and Low before evaluating new signals.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        fee_rate: float = 0.001,      # 0.1% per transaction
        slippage: float = 0.0005,    # 5 basis points
        position_size_pct: float = 0.95,  # 95% capital allocation
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None,
    ):
        self.initial_capital = float(initial_capital)
        self.fee_rate = float(fee_rate)
        self.slippage = float(slippage)
        self.position_size_pct = float(position_size_pct)
        self.stop_loss_pct = float(stop_loss_pct) if stop_loss_pct else None
        self.take_profit_pct = float(take_profit_pct) if take_profit_pct else None

    def run(
        self,
        strategy: BaseStrategy,
        ohlcv_df: pl.DataFrame,
        symbol: str = "ASSET",
        news_sentiment: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes event-driven simulation over chronological candles.
        
        Args:
            strategy: BaseStrategy instance.
            ohlcv_df: Polars DataFrame sorted chronologically with columns:
                      ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
            symbol: Ticker symbol being simulated.
            news_sentiment: Optional news sentiment list.
            
        Returns:
            Dict containing:
                - 'metrics': Quantitative performance summary.
                - 'equity_curve': Array of candle-by-candle equity data points.
                - 'trades': Complete list of completed round-trip trades.
                - 'final_equity': Ending portfolio balance.
        """
        if ohlcv_df.height < 5:
            raise ValueError(f"Insufficient historical data ({ohlcv_df.height} bars) for backtesting.")

        # Ensure sorted chronologically
        df = ohlcv_df.sort("timestamp")

        # 1. Generate signals (candle t evaluated on close t)
        df_with_signals = strategy.generate_signals(df, news_sentiment=news_sentiment)
        
        # Verify signal column exists
        if "signal" not in df_with_signals.columns:
            raise ValueError("Strategy failed to generate required 'signal' column.")

        # Extract rows for event-driven simulation
        rows = df_with_signals.to_dicts()
        num_candles = len(rows)

        # Portfolio state
        cash = self.initial_capital
        position_shares = 0.0
        position_entry_price = 0.0
        position_entry_time: Optional[datetime] = None
        accumulated_fees = 0.0

        equity_curve: List[Dict[str, Any]] = []
        trades: List[Dict[str, Any]] = []
        trade_counter = 1

        pending_signal = 0  # Signal generated on candle t to be executed on candle t+1

        for i in range(num_candles):
            candle = rows[i]
            timestamp = candle["timestamp"]
            open_p = float(candle["open"])
            high_p = float(candle["high"])
            low_p = float(candle["low"])
            close_p = float(candle["close"])

            # -------------------------------------------------------------
            # STEP A: Check Stop-Loss and Take-Profit for existing open position
            # -------------------------------------------------------------
            position_closed_this_bar = False

            if position_shares > 0:
                stop_triggered = False
                tp_triggered = False
                exit_price = 0.0
                exit_reason = ""

                # Check Stop Loss (Low <= entry * (1 - stop_loss_pct))
                if self.stop_loss_pct is not None:
                    stop_level = position_entry_price * (1.0 - self.stop_loss_pct)
                    if low_p <= stop_level:
                        stop_triggered = True
                        # Fill at stop level minus slippage
                        exit_price = max(stop_level * (1.0 - self.slippage), low_p)
                        exit_reason = "stop_loss"

                # Check Take Profit (High >= entry * (1 + take_profit_pct))
                if not stop_triggered and self.take_profit_pct is not None:
                    tp_level = position_entry_price * (1.0 + self.take_profit_pct)
                    if high_p >= tp_level:
                        tp_triggered = True
                        # Fill at take profit level minus slippage
                        exit_price = min(tp_level * (1.0 - self.slippage), high_p)
                        exit_reason = "take_profit"

                if stop_triggered or tp_triggered:
                    gross_revenue = position_shares * exit_price
                    fee = gross_revenue * self.fee_rate
                    net_revenue = gross_revenue - fee
                    cash += net_revenue
                    accumulated_fees += fee

                    cost_basis = position_shares * position_entry_price
                    realized_pnl = net_revenue - cost_basis
                    pnl_pct = (exit_price - position_entry_price) / position_entry_price if position_entry_price > 0 else 0.0

                    trades.append({
                        "id": trade_counter,
                        "symbol": symbol,
                        "side": "long",
                        "entry_time": position_entry_time,
                        "exit_time": timestamp,
                        "entry_price": round(position_entry_price, 4),
                        "exit_price": round(exit_price, 4),
                        "size": round(position_shares, 4),
                        "fee": round(fee, 2),
                        "slippage": round(abs(exit_price - (position_entry_price * (1 - self.stop_loss_pct if stop_triggered else 1 + self.take_profit_pct))), 4),
                        "realized_pnl": round(realized_pnl, 2),
                        "pnl_percentage": round(pnl_pct * 100.0, 2),
                        "exit_reason": exit_reason
                    })
                    trade_counter += 1

                    position_shares = 0.0
                    position_entry_price = 0.0
                    position_entry_time = None
                    position_closed_this_bar = True

            # -------------------------------------------------------------
            # STEP B: Execute Pending Signal from Previous Candle (candle t-1)
            # ZERO LOOK-AHEAD BIAS: Fills strictly at current candle OPEN price
            # -------------------------------------------------------------
            if not position_closed_this_bar and pending_signal != 0:
                if pending_signal == 1 and position_shares == 0:
                    # LONG ENTRY at Open + Slippage
                    fill_price = open_p * (1.0 + self.slippage)
                    alloc_cash = cash * self.position_size_pct
                    shares_to_buy = alloc_cash / fill_price if fill_price > 0 else 0.0
                    
                    if shares_to_buy > 0:
                        gross_cost = shares_to_buy * fill_price
                        fee = gross_cost * self.fee_rate
                        total_cost = gross_cost + fee
                        
                        if cash >= total_cost:
                            cash -= total_cost
                            accumulated_fees += fee
                            position_shares = shares_to_buy
                            position_entry_price = fill_price
                            position_entry_time = timestamp

                elif pending_signal == -1 and position_shares > 0:
                    # LONG EXIT at Open - Slippage
                    fill_price = open_p * (1.0 - self.slippage)
                    gross_revenue = position_shares * fill_price
                    fee = gross_revenue * self.fee_rate
                    net_revenue = gross_revenue - fee
                    cash += net_revenue
                    accumulated_fees += fee

                    cost_basis = position_shares * position_entry_price
                    realized_pnl = net_revenue - cost_basis
                    pnl_pct = (fill_price - position_entry_price) / position_entry_price if position_entry_price > 0 else 0.0

                    trades.append({
                        "id": trade_counter,
                        "symbol": symbol,
                        "side": "long",
                        "entry_time": position_entry_time,
                        "exit_time": timestamp,
                        "entry_price": round(position_entry_price, 4),
                        "exit_price": round(fill_price, 4),
                        "size": round(position_shares, 4),
                        "fee": round(fee, 2),
                        "slippage": round(abs(open_p - fill_price), 4),
                        "realized_pnl": round(realized_pnl, 2),
                        "pnl_percentage": round(pnl_pct * 100.0, 2),
                        "exit_reason": "signal"
                    })
                    trade_counter += 1

                    position_shares = 0.0
                    position_entry_price = 0.0
                    position_entry_time = None

            # Reset pending signal once evaluated
            pending_signal = 0

            # -------------------------------------------------------------
            # STEP C: Evaluate and Queue Strategy Signal for NEXT candle
            # (Signal computed on candle t close -> executed on candle t+1 open)
            # -------------------------------------------------------------
            curr_signal = int(candle.get("signal", 0))
            if curr_signal in (1, -1):
                pending_signal = curr_signal

            # -------------------------------------------------------------
            # STEP D: Mark Portfolio to Market at Candle Close
            # -------------------------------------------------------------
            position_market_value = position_shares * close_p
            unrealized_pnl = (position_market_value - (position_shares * position_entry_price)) if position_shares > 0 else 0.0
            current_equity = cash + position_market_value

            equity_curve.append({
                "timestamp": timestamp,
                "equity": round(current_equity, 2),
                "cash": round(cash, 2),
                "positions_value": round(position_market_value, 2),
                "position_size": round(position_shares, 4),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "close": close_p
            })

        # -------------------------------------------------------------
        # STEP E: Close any remaining open position on final candle close
        # -------------------------------------------------------------
        if position_shares > 0:
            final_candle = rows[-1]
            final_time = final_candle["timestamp"]
            final_price = float(final_candle["close"]) * (1.0 - self.slippage)
            gross_revenue = position_shares * final_price
            fee = gross_revenue * self.fee_rate
            net_revenue = gross_revenue - fee
            cash += net_revenue
            accumulated_fees += fee

            cost_basis = position_shares * position_entry_price
            realized_pnl = net_revenue - cost_basis
            pnl_pct = (final_price - position_entry_price) / position_entry_price if position_entry_price > 0 else 0.0

            trades.append({
                "id": trade_counter,
                "symbol": symbol,
                "side": "long",
                "entry_time": position_entry_time,
                "exit_time": final_time,
                "entry_price": round(position_entry_price, 4),
                "exit_price": round(final_price, 4),
                "size": round(position_shares, 4),
                "fee": round(fee, 2),
                "slippage": round(abs(float(final_candle["close"]) - final_price), 4),
                "realized_pnl": round(realized_pnl, 2),
                "pnl_percentage": round(pnl_pct * 100.0, 2),
                "exit_reason": "end_of_data"
            })
            trade_counter += 1
            position_shares = 0.0

        final_equity = cash
        benchmark_initial = float(rows[0]["open"])
        benchmark_final = float(rows[-1]["close"])

        # Calculate institutional metrics
        metrics = PerformanceMetricsCalculator.calculate(
            initial_capital=self.initial_capital,
            final_equity=final_equity,
            equity_curve=equity_curve,
            trades=trades,
            benchmark_initial_price=benchmark_initial,
            benchmark_final_price=benchmark_final
        )

        return {
            "symbol": symbol,
            "initial_capital": self.initial_capital,
            "final_equity": round(final_equity, 2),
            "total_fees_paid": round(accumulated_fees, 2),
            "metrics": metrics,
            "trades": trades,
            "equity_curve": equity_curve,
        }

