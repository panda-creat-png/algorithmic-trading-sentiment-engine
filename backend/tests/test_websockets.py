import pytest
from starlette.testclient import TestClient
from app.main import app
from app.websockets.market_ws import market_ws_manager


@pytest.fixture(autouse=True)
def clean_ws_state():
    yield
    # Cleanup after each test
    client = TestClient(app)
    # Ensure manager collections are clean


def test_websocket_market_symbol_snapshot_and_tick():
    """Tests connecting to /ws/market/{symbol}, receiving initial snapshot and subsequent ticks."""
    client = TestClient(app)
    with client.websocket_connect("/ws/market/AAPL") as websocket:
        # First message must be snapshot
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "snapshot"
        assert snapshot["symbol"] == "AAPL"
        assert "data" in snapshot
        assert "price" in snapshot["data"]

        # Subsequent message should be tick stream
        tick = websocket.receive_json()
        assert tick["type"] in ("tick", "snapshot")
        if tick["type"] == "tick":
            assert tick["symbol"] == "AAPL"
            assert "price" in tick
            assert "bid" in tick
            assert "ask" in tick
            assert "timestamp" in tick


def test_websocket_ping_pong():
    """Tests client heartbeat ping/pong over WebSocket."""
    client = TestClient(app)
    with client.websocket_connect("/ws/market/NVDA") as websocket:
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "snapshot"

        # Plain text ping
        websocket.send_text("ping")
        pong = websocket.receive_json()
        assert pong["type"] == "pong"
        assert "timestamp" in pong

        # JSON action ping
        websocket.send_json({"action": "ping"})
        pong2 = websocket.receive_json()
        assert pong2["type"] == "pong"


def test_websocket_dynamic_subscribe_and_unsubscribe():
    """Tests multi-asset WebSocket endpoint with dynamic subscribe/unsubscribe."""
    client = TestClient(app)
    with client.websocket_connect("/ws/market") as websocket:
        # Subscribe to BTC-USD
        websocket.send_json({"action": "subscribe", "symbol": "BTC-USD"})
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "snapshot"
        assert snapshot["symbol"] == "BTC-USD"

        # Unsubscribe
        websocket.send_json({"action": "unsubscribe", "symbol": "BTC-USD"})
        # Send ping to confirm connection is still alive and responsive
        websocket.send_text("ping")
        pong = websocket.receive_json()
        assert pong["type"] == "pong"


def test_api_v1_market_websocket_endpoint():
    """Tests the /api/v1/market/ws/{symbol} router endpoint."""
    client = TestClient(app)
    with client.websocket_connect("/api/v1/market/ws/MSFT") as websocket:
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "snapshot"
        assert snapshot["symbol"] == "MSFT"
        assert "data" in snapshot
