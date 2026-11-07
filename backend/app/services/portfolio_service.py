from datetime import datetime, timezone
from typing import Dict, Any, List
from app.services.market_data_service import market_data_service
from app.schemas.portfolio import PortfolioOverview, PositionModel


class PaperPortfolioService:
    """
    Real-Time Institutional Paper Trading & Portfolio Simulator Service.
    Maintains mark-to-market positions, liquid cash, and realized/unrealized P&L.
    """

    INITIAL_CAPITAL = 100000.0

    def __init__(self):
        self.cash_balance = 35000.0
        self.realized_pnl = 8450.0
        self.positions: Dict[str, Dict[str, float]] = {
            "NVDA": {"quantity": 100.0, "average_entry_price": 118.50},
            "AAPL": {"quantity": 80.0, "average_entry_price": 218.00},
            "BTC-USD": {"quantity": 0.5, "average_entry_price": 64200.00},
        }

    async def get_overview(self) -> PortfolioOverview:
        """Computes live mark-to-market portfolio overview using real quotes."""
        position_models: List[PositionModel] = []
        total_market_value = 0.0
        total_unrealized_pnl = 0.0

        for symbol, pos in list(self.positions.items()):
            qty = pos["quantity"]
            if qty <= 1e-6:
                continue

            avg_entry = pos["average_entry_price"]
            
            # Fetch live quote
            try:
                quote = await market_data_service.get_quote(symbol)
                current_price = float(quote.get("price", avg_entry))
            except Exception:
                current_price = avg_entry

            mkt_val = qty * current_price
            unrealized = mkt_val - (qty * avg_entry)
            unrealized_pct = (unrealized / (qty * avg_entry)) * 100.0 if (qty * avg_entry) > 0 else 0.0

            total_market_value += mkt_val
            total_unrealized_pnl += unrealized

            position_models.append(PositionModel(
                symbol=symbol,
                quantity=round(qty, 4),
                average_entry_price=round(avg_entry, 2),
                current_price=round(current_price, 2),
                market_value=round(mkt_val, 2),
                unrealized_pnl=round(unrealized, 2),
                unrealized_pnl_pct=round(unrealized_pct, 2)
            ))

        total_equity = self.cash_balance + total_market_value
        total_return_pct = ((total_equity - self.INITIAL_CAPITAL) / self.INITIAL_CAPITAL) * 100.0

        return PortfolioOverview(
            total_equity=round(total_equity, 2),
            cash_balance=round(self.cash_balance, 2),
            unrealized_pnl=round(total_unrealized_pnl, 2),
            realized_pnl=round(self.realized_pnl, 2),
            total_return_pct=round(total_return_pct, 2),
            positions=position_models,
            timestamp=datetime.now(timezone.utc)
        )

    async def execute_order(self, symbol: str, side: str, quantity: float) -> PortfolioOverview:
        """Executes a paper order and marks portfolio to market."""
        sym_clean = symbol.upper()
        quote = await market_data_service.get_quote(sym_clean)
        price = float(quote.get("price", 100.0))
        side_clean = side.lower()

        if side_clean == "buy":
            total_cost = quantity * price
            if self.cash_balance < total_cost:
                raise ValueError(f"Insufficient cash balance (${self.cash_balance:,.2f}) for order cost (${total_cost:,.2f}).")
            
            self.cash_balance -= total_cost
            if sym_clean in self.positions:
                existing = self.positions[sym_clean]
                old_qty = existing["quantity"]
                old_avg = existing["average_entry_price"]
                new_qty = old_qty + quantity
                new_avg = ((old_qty * old_avg) + (quantity * price)) / new_qty
                self.positions[sym_clean] = {"quantity": new_qty, "average_entry_price": new_avg}
            else:
                self.positions[sym_clean] = {"quantity": quantity, "average_entry_price": price}

        elif side_clean == "sell":
            if sym_clean not in self.positions or self.positions[sym_clean]["quantity"] < quantity:
                available = self.positions.get(sym_clean, {}).get("quantity", 0.0)
                raise ValueError(f"Cannot sell {quantity} of {sym_clean}; only {available} available in portfolio.")

            existing = self.positions[sym_clean]
            avg_entry = existing["average_entry_price"]
            revenue = quantity * price
            realized = (price - avg_entry) * quantity

            self.cash_balance += revenue
            self.realized_pnl += realized

            new_qty = existing["quantity"] - quantity
            if new_qty <= 1e-6:
                del self.positions[sym_clean]
            else:
                existing["quantity"] = new_qty

        else:
            raise ValueError(f"Invalid order side '{side}'. Must be 'buy' or 'sell'.")

        return await self.get_overview()

    def reset_portfolio(self) -> None:
        """Resets paper portfolio to $100,000 cash balance."""
        self.cash_balance = self.INITIAL_CAPITAL
        self.realized_pnl = 0.0
        self.positions.clear()


portfolio_service = PaperPortfolioService()

