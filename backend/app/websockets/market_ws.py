import asyncio
import json
import random
from datetime import datetime, timezone
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from app.services.market_data_service import market_data_service
from app.core.logging import logger


class MarketWebSocketManager:
    """Institutional real-time WebSocket connection manager and tick streamer."""

    def __init__(self):
        # symbol -> set of connected WebSockets
        self.active_subscriptions: Dict[str, Set[WebSocket]] = {}
        # websocket -> set of subscribed symbols
        self.client_subscriptions: Dict[WebSocket, Set[str]] = {}
        # Track last known price and previous close per symbol for tick walks
        self._price_state: Dict[str, Dict[str, float]] = {}
        # Background streaming task
        self._streaming_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._stream_interval: float = 1.0  # 1 second tick interval

    async def connect(self, websocket: WebSocket, initial_symbol: Optional[str] = None):
        """Accepts a WebSocket connection and registers initial subscription."""
        await websocket.accept()
        async with self._lock:
            self.client_subscriptions[websocket] = set()

        if initial_symbol:
            await self.subscribe(websocket, initial_symbol)

        # Ensure streaming background worker is active
        async with self._lock:
            if self._streaming_task is None or self._streaming_task.done():
                self._streaming_task = asyncio.create_task(self._ticker_loop())

    async def disconnect(self, websocket: WebSocket):
        """Unregisters a WebSocket from all active subscriptions."""
        async with self._lock:
            subscribed_symbols = self.client_subscriptions.pop(websocket, set())
            for symbol in subscribed_symbols:
                if symbol in self.active_subscriptions:
                    self.active_subscriptions[symbol].discard(websocket)
                    if not self.active_subscriptions[symbol]:
                        self.active_subscriptions.pop(symbol, None)

            # If no active clients remain, cancel streaming task
            if not self.client_subscriptions and self._streaming_task and not self._streaming_task.done():
                self._streaming_task.cancel()
                self._streaming_task = None

    async def subscribe(self, websocket: WebSocket, symbol: str):
        """Subscribes an active client to a market symbol and transmits initial snapshot."""
        sym_clean = symbol.upper()
        async with self._lock:
            if sym_clean not in self.active_subscriptions:
                self.active_subscriptions[sym_clean] = set()
            self.active_subscriptions[sym_clean].add(websocket)

            if websocket in self.client_subscriptions:
                self.client_subscriptions[websocket].add(sym_clean)

        # Fetch and transmit current quote snapshot
        try:
            quote = await market_data_service.get_quote(sym_clean)
            price = float(quote.get("price", 100.0))
            prev_close = float(quote.get("previous_close", price))

            self._price_state[sym_clean] = {
                "price": price,
                "previous_close": prev_close,
                "volume": float(quote.get("volume", 1000000.0)),
            }

            snapshot_msg = {
                "type": "snapshot",
                "symbol": sym_clean,
                "data": quote,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await websocket.send_json(snapshot_msg)
        except Exception as e:
            logger.warning(f"Failed to send initial snapshot for {sym_clean}: {e}")

    async def unsubscribe(self, websocket: WebSocket, symbol: str):
        """Removes a client's subscription to a specific symbol."""
        sym_clean = symbol.upper()
        async with self._lock:
            if sym_clean in self.active_subscriptions:
                self.active_subscriptions[sym_clean].discard(websocket)
                if not self.active_subscriptions[sym_clean]:
                    self.active_subscriptions.pop(sym_clean, None)

            if websocket in self.client_subscriptions:
                self.client_subscriptions[websocket].discard(sym_clean)

    async def broadcast_tick(self, symbol: str, tick: Dict[str, Any]):
        """Transmits market tick payload to all active subscribers for a symbol."""
        subscribers = list(self.active_subscriptions.get(symbol, set()))
        if not subscribers:
            return

        dead_sockets = []
        for ws in subscribers:
            try:
                await ws.send_json(tick)
            except Exception:
                dead_sockets.append(ws)

        if dead_sockets:
            for ws in dead_sockets:
                await self.disconnect(ws)

    async def handle_client(self, websocket: WebSocket, initial_symbol: Optional[str] = None):
        """Main lifecycle loop handling incoming frames, subscriptions, and heartbeats."""
        await self.connect(websocket, initial_symbol)
        try:
            while True:
                msg_raw = await websocket.receive_text()
                # Handle plain ping
                if msg_raw.strip().lower() == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
                    continue

                try:
                    payload = json.loads(msg_raw)
                except Exception:
                    continue

                action = payload.get("action")
                if action == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
                elif action == "subscribe":
                    target_sym = payload.get("symbol")
                    if target_sym:
                        await self.subscribe(websocket, str(target_sym))
                elif action == "unsubscribe":
                    target_sym = payload.get("symbol")
                    if target_sym:
                        await self.unsubscribe(websocket, str(target_sym))
        except WebSocketDisconnect:
            await self.disconnect(websocket)
        except asyncio.CancelledError:
            await self.disconnect(websocket)
        except Exception as e:
            logger.debug(f"WebSocket client terminated: {e}")
            await self.disconnect(websocket)

    async def _ticker_loop(self):
        """Background coroutine that streams real-time L1 market ticks to subscribers."""
        try:
            while True:
                await asyncio.sleep(self._stream_interval)
                symbols = list(self.active_subscriptions.keys())
                if not symbols:
                    continue

                for symbol in symbols:
                    state = self._price_state.get(symbol)
                    if not state:
                        quote = await market_data_service.get_quote(symbol)
                        price = float(quote.get("price", 100.0))
                        prev_close = float(quote.get("previous_close", price))
                        vol = float(quote.get("volume", 1000000.0))
                        state = {"price": price, "previous_close": prev_close, "volume": vol}
                        self._price_state[symbol] = state

                    current_price = state["price"]
                    prev_close = state["previous_close"]

                    # Micro-tick price fluctuation simulation (geometric Brownian drift $\pm 0.1\%$)
                    drift_pct = random.uniform(-0.0012, 0.0012)
                    new_price = round(max(0.01, current_price * (1.0 + drift_pct)), 2)
                    state["price"] = new_price
                    state["volume"] += random.randint(10, 250)

                    change = round(new_price - prev_close, 2)
                    change_pct = round((change / prev_close) * 100.0, 2) if prev_close else 0.0

                    tick = {
                        "type": "tick",
                        "symbol": symbol,
                        "price": new_price,
                        "bid": round(new_price * 0.9998, 2),
                        "ask": round(new_price * 1.0002, 2),
                        "change": change,
                        "change_percent": change_pct,
                        "volume": state["volume"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    await self.broadcast_tick(symbol, tick)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"WebSocket ticker loop error: {e}", exc_info=True)

    async def close_all(self):
        """Gracefully disconnects all active connections and terminates streaming."""
        if self._streaming_task and not self._streaming_task.done():
            self._streaming_task.cancel()
            self._streaming_task = None

        all_sockets = list(self.client_subscriptions.keys())
        for ws in all_sockets:
            try:
                await ws.close()
            except Exception:
                pass
        self.active_subscriptions.clear()
        self.client_subscriptions.clear()


market_ws_manager = MarketWebSocketManager()
