# QuantMind AI - System Issues & Status Tracker

This document tracks all known technical issues, architectural limitations, security vulnerabilities, and bug statuses across the **QuantMind AI** algorithmic trading platform.

---

## 📊 Summary Status Dashboard

| Total Issues Tracked | ❌ Open / Not Fixed | ⚠️ Partial / Workaround | ✅ Resolved / Fixed |
| :---: | :---: | :---: | :---: |
| **16** | **5** | **3** | **8** |

---

## 📋 Comprehensive Issues Matrix

| ID | Issue & Component | Category | Severity | Status | Target Version / Phase |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **ISS-01** | Empty candle response schema mismatch in `/market/{symbol}/indicators` | Backend API | **CRITICAL** | ✅ **FIXED** | Verified E2E Pipeline |
| **ISS-02** | In-Memory Portfolio state reset on backend restart (`portfolio_service.py`) | Database / State | **HIGH** | ❌ **NOT FIXED** | Phase 6.1 |
| **ISS-03** | Yahoo Finance (`yfinance`) rate-limiting without database fallback | Data Pipeline | **HIGH** | ❌ **NOT FIXED** | Phase 6.2 |
| **ISS-04** | Redis 2-3s connection timeout delay on local dev startup without Docker | Infrastructure | **MEDIUM** | ⚠️ **PARTIAL** | Phase 6.2 |
| **ISS-05** | SQLite `database is locked` concurrency risk under async load | Database | **MEDIUM** | ⚠️ **PARTIAL** | Phase 6.2 |
| **ISS-06** | Frontend bundle size warning (>500 kB `index.js`, missing `React.lazy`) | Frontend | **MEDIUM** | ❌ **NOT FIXED** | Phase 6.3 |
| **ISS-07** | Hardcoded default JWT `SECRET_KEY` in `config.py` | Security | **HIGH** | ❌ **NOT FIXED** | Phase 6.1 |
| **ISS-08** | Lack of WebSockets for real-time tick-by-tick market data streaming | Architecture | **LOW** | ❌ **NOT FIXED** | Backlog / Phase 7 |
| **ISS-09** | FinBERT CPU inference latency (1-3s) & memory consumption (~1GB) | AI Engine | **MEDIUM** | ⚠️ **PARTIAL** | Phase 6.3 |
| **ISS-10** | External Alpaca API credentials required for real broker order execution | Brokerage | **INFO** | ℹ️ **CONFIG PENDING** | User Setup |
| **ISS-11** | React child object rendering crash in Quantitative Signals card | Frontend UI | **HIGH** | ✅ **FIXED** | Verified (`aa78771`) |
| **ISS-12** | Chart crosshair cursor snapping/stopping on candlesticks (Magnet mode) | Frontend Chart | **MEDIUM** | ✅ **FIXED** | Verified (`4d9a736`) |
| **ISS-13** | Bottom drag & zoom helper hint overlay obstructing chart axis | Frontend UI | **LOW** | ✅ **FIXED** | Verified (`29c1380`) |
| **ISS-14** | Chart Fullscreen expanded view missing | Frontend UI | **MEDIUM** | ✅ **FIXED** | Verified (`f73c4f7`) |
| **ISS-15** | AI Trade Autopsy & Attribution Engine ("Why won / Why lost") missing | Quant Diagnostics | **HIGH** | ✅ **FIXED** | Verified (`87d534c`) |
| **ISS-16** | Trade Autopsy UI labels localization to institutional English | Internationalization | **LOW** | ✅ **FIXED** | Verified (`5ee531f`) |

---

## 🔍 Detailed Issues Breakdown

### 🔴 1. Open / Not Fixed Issues (Active Priority)

#### `ISS-02`: In-Memory Paper Portfolio State Reset on Server Restart
- **Component**: [`backend/app/services/portfolio_service.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/services/portfolio_service.py#L23-L50)
- **Status**: ❌ **NOT FIXED**
- **Severity**: **HIGH**
- **Symptom**:
  `self.positions`, `self.cash_balance`, and `self.trade_history` are stored as pure in-memory Python dictionaries inside the singleton `PaperPortfolioService`.
- **Impact**:
  Whenever the backend server is restarted or deployed across multiple Uvicorn workers, all paper trading orders and P&L history executed by the user are permanently lost and reset to the seed values.
- **Recommended Action**:
  Create SQLAlchemy ORM models (`PortfolioPosition` and `PortfolioTrade`) and migrate `PaperPortfolioService` to read/write from PostgreSQL/SQLite.

---

#### `ISS-03`: Yahoo Finance (`yfinance`) Rate Limits & Lack of Local DB Fallback
- **Component**: [`backend/app/data_pipeline/yahoo_provider.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/yahoo_provider.py)
- **Status**: ❌ **NOT FIXED**
- **Severity**: **HIGH**
- **Symptom**:
  `yfinance` frequently emits:
  `ERROR yfinance:history.py:378 $NVDA: possibly delisted; no price data found` due to IP throttling by Yahoo servers.
- **Impact**:
  Candles fail to load for popular tickers when multiple requests are triggered rapidly.
- **Recommended Action**:
  Implement a local database historical fallback in `MarketDataService`: if `provider.fetch_ohlcv()` returns empty or errors, query existing candles stored in the local database or return cached data instead of failing.

---

#### `ISS-06`: Frontend Bundle Size Warning (>500 kB Minified Chunk)
- **Component**: [`frontend/src/App.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/App.tsx)
- **Status**: ❌ **NOT FIXED**
- **Severity**: **MEDIUM**
- **Symptom**:
  Vite production build emits:
  `(!) Some chunks are larger than 500 kB after minification (dist/assets/index-*.js: 633.5 kB)`.
- **Impact**:
  Initial page load loads the entire application bundle at once, degrading initial Time-to-Interactive (TTI).
- **Recommended Action**:
  Implement `React.lazy` and `Suspense` route-based code splitting for heavyweight pages: `AssetDetails`, `Backtesting`, `NewsSentiment`, `PortfolioSimulator`, and `PerformanceAnalytics`.

---

#### `ISS-07`: Hardcoded Default JWT `SECRET_KEY` in `config.py`
- **Component**: [`backend/app/core/config.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/core/config.py#L21)
- **Status**: ❌ **NOT FIXED**
- **Severity**: **HIGH (Security)**
- **Symptom**:
  `SECRET_KEY` defaults to a known development string:
  `"quantmind-ai-super-secret-development-jwt-key-replace-in-production"`.
- **Impact**:
  If a production deployment runs without an explicit `.env` setting, JWT tokens could theoretically be forged.
- **Recommended Action**:
  Enforce a validation error in `Settings` if `ENVIRONMENT == "production"` and `SECRET_KEY` matches the default development key.

---

#### `ISS-08`: Absence of Real-Time WebSocket Streaming (L1 Ticks)
- **Component**: [`backend/app/main.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/main.py), [`frontend/src/services/api.ts`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/services/api.ts)
- **Status**: ❌ **NOT FIXED**
- **Severity**: **LOW**
- **Symptom**:
  All market quotes and order book updates are fetched via REST HTTP Polling.
- **Impact**:
  Sub-second price updates are not streaming continuously without manual user refresh or polling timers.
- **Recommended Action**:
  Introduce a FastAPI WebSocket route (`/ws/market/{symbol}`) and connect it to a frontend WebSocket hook.

---

### ⚠️ 2. Partial / Workaround Issues

#### `ISS-04`: Redis Connection Timeout on Startup
- **Component**: [`backend/app/core/redis.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/core/redis.py)
- **Status**: ⚠️ **PARTIAL WORKAROUND ACTIVE**
- **Current Behavior**:
  When Redis is not running locally, the system times out after 2-3 seconds, logs a warning, and gracefully falls back to `self.memory_cache`.
- **Limitation**:
  The initial request startup experiences an unnecessary 2-3 second delay.

---

#### `ISS-05`: SQLite Concurrency Constraints in Development
- **Component**: [`backend/app/core/database.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/core/database.py)
- **Status**: ⚠️ **PARTIAL**
- **Current Behavior**:
  Development uses SQLite (`sqlite+aiosqlite:///./quantmind.db`). Under simultaneous background news ingestion, backtest persistence, and market caching, SQLite can raise `database is locked`.
- **Limitation**:
  Full PostgreSQL is configured in `docker-compose.yml`, but local raw Python development still uses SQLite by default.

---

#### `ISS-09`: FinBERT CPU Inference Overhead
- **Component**: [`backend/app/sentiment/finbert_engine.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/sentiment/finbert_engine.py)
- **Status**: ⚠️ **PARTIAL WORKAROUND ACTIVE**
- **Current Behavior**:
  If HuggingFace/PyTorch fails or environment is offline, the engine falls back to a zero-latency Loughran-McDonald dictionary.
- **Limitation**:
  When FinBERT runs on CPU, it consumes ~1GB RAM and requires 1-3s per headline batch.

---

### ✅ 3. Resolved Issues (Successfully Fixed)

#### `ISS-01`: Empty Candle Response Schema Mismatch in `/indicators`
- **Component**: [`backend/app/api/v1/endpoints/market.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/api/v1/endpoints/market.py), [`backend/app/indicators/technical_engine.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/indicators/technical_engine.py), [`backend/app/data_pipeline/yahoo_provider.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/yahoo_provider.py)
- **Status**: ✅ **FIXED**
- **Resolution**:
  - Updated `/api/v1/market/{symbol}/indicators` to always return full consistent schema (`symbol`, `timeframe`, `status: "empty"`, `total_candles: 0`, `bias: "NEUTRAL"`, `net_score: 0.0`, `signals: []`, `latest_metrics: {}`) even when candles are empty.
  - Hardened `technical_engine.generate_signals` to always output `bias`, `net_score`, `signals`, and `latest_metrics` when `len(df) < 2`.
  - Added adaptive fallback periods (`2y`, `1y`, `6mo`, `1mo`) in `_fetch_yfinance_history` to bypass Yahoo Finance rate-limiting on historical requests.
  - Fully verified: `backend/tests/test_e2e_pipeline.py` passed 100%.

---

#### `ISS-11`: React Child Object Rendering Crash
- **Component**: [`frontend/src/pages/AssetDetails.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/AssetDetails.tsx)
- **Status**: ✅ **FIXED** (`commit aa78771`)
- **Resolution**:
  Destructured technical signal dictionary objects (`type`, `indicator`, `signal`, `strength`) into styled JSX badges instead of passing raw objects as React children.

---

#### `ISS-12`: Candlestick Crosshair Magnet Sticking/Snapping
- **Component**: [`frontend/src/charts/LightweightCandleChart.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/charts/LightweightCandleChart.tsx)
- **Status**: ✅ **FIXED** (`commit 4d9a736`)
- **Resolution**:
  Configured `crosshair: { mode: CrosshairMode.Normal }` so crosshairs track cursor coordinates smoothly in 2D space without snapping to candlestick bars.

---

#### `ISS-13`: Bottom Drag & Zoom Hint Overlay Removal
- **Component**: [`frontend/src/charts/LightweightCandleChart.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/charts/LightweightCandleChart.tsx)
- **Status**: ✅ **FIXED** (`commit 29c1380`)
- **Resolution**:
  Completely removed the floating compass helper hint pill that was obstructing the bottom volume bars and time scale.

---

#### `ISS-14`: Chart Fullscreen Mode
- **Component**: [`frontend/src/pages/AssetDetails.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/AssetDetails.tsx)
- **Status**: ✅ **FIXED** (`commit f73c4f7`)
- **Resolution**:
  Added an intuitive 1-click Fullscreen toggle with keyboard `ESC` shortcut to expand TradingView charts across the entire monitor.

---

#### `ISS-15`: AI Trade Autopsy & Attribution Engine ("Why won / Why lost")
- **Component**: [`backend/app/services/portfolio_service.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/services/portfolio_service.py), [`frontend/src/pages/PortfolioSimulator.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/PortfolioSimulator.tsx)
- **Status**: ✅ **FIXED** (`commit 87d534c`)
- **Resolution**:
  Built an automated post-trade attribution engine providing technical indicator reasons, FinBERT sentiment catalyst breakdown, risk discipline grading, and actionable lessons learned for every trade.

---

#### `ISS-16`: Trade Autopsy UI Institutional English Localization
- **Component**: [`frontend/src/pages/PortfolioSimulator.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/PortfolioSimulator.tsx)
- **Status**: ✅ **FIXED** (`commit 5ee531f`)
- **Resolution**:
  Standardized all diagnostic UI labels to institutional quantitative trading terminology (`Why This Trade Won`, `Why This Trade Lost`, `AI Trade Diagnostics & Autopsy`).

---

*Last Updated: 2026-11-20 | Maintained by Antigravity AI Engine*
