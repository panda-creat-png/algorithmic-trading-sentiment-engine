# QuantMind AI - Development Roadmap & Phase Tracking

This document tracks implementation status, architectural milestones, verified environments, and the phase-by-phase roadmap for QuantMind AI.

---

## 🎯 Phase Tracking Status

| Phase | Description | Status | Verification & Test Coverage |
| :--- | :--- | :---: | :--- |
| **Phase 1** | **Environment Inspection, Foundation Architecture, PostgreSQL, Redis, Backend & Frontend Initialization** | **COMPLETED ✅** | Async DB session, live Redis caching, 6/6 Pytest tests passed, React 19 + TypeScript build passed |
| **Phase 2** | **Market Data Pipeline (Yahoo Finance, Alpaca, OHLCV, Polars data engine, Cache & Validation)** | **COMPLETED ✅** | Real live OHLCV ingestion, Polars 2.1 validation, TradingView Lightweight Charts, 15/15 Pytest tests passed |
| **Phase 3** | **AI Financial Sentiment Engine (FinBERT) & Polars Technical Analysis Engine** | **COMPLETED ✅** | FinBERT cached & verified, Polars technical indicators & signals, live news ingestion, sentiment correlation, 27/27 Pytest tests passed |
| **Phase 4** | **Algorithmic Strategy Builder & Event-Driven Backtesting Engine** | **COMPLETED ✅** | 7 modular quant strategies, strict zero look-ahead bias engine, slippage/fee modeling, 34/34 Pytest tests passed, React equity curve |
| **Phase 5** | Interactive Institutional Dashboard (TradingView lightweight charts, live overview, heatmaps) | *Pending User Approval* | Next milestone |
| **Phase 6** | Security, Authentication (JWT), End-to-End Testing, Optimization & Production Deployment | *Pending* | - |

---

## 📋 Completed Tasks (Phase 2: Market Data Pipeline)

### 1. Ingestion Providers Architecture
- Created [`BaseDataProvider`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/base.py) abstract interface defining `fetch_ohlcv`, `get_supported_timeframes`, and `get_latest_quote`.
- Implemented [`YahooFinanceProvider`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/yahoo_provider.py):
  - Ingests real historical market candles across all timeframes: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, `1wk`.
  - Resamples `1h` bars into `4h` bars natively in Polars.
  - Implemented asynchronous non-blocking thread execution for external I/O with exponential backoff retry.
  - Normalizes timestamps to strict UTC Python datetimes to eliminate NumPy resolution mismatches.
  - Real-time quote fetching (`get_latest_quote`) returning current price, change, change percentage, day high/low, and 52-week ranges.
- Implemented [`CryptoDataProvider`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/crypto_provider.py):
  - Specialized 24/7 continuous crypto markets handling (`BTC-USD`, `ETH-USD`, `SOL-USD`).
- Implemented [`AlpacaProvider`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/alpaca_provider.py):
  - Optional provider fallback when API credentials are provided.

### 2. High-Performance Polars Data Validation Engine
- Implemented [`DataValidationService`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/validation.py):
  - `validate_ohlc_integrity`: Enforces price geometry (`High >= Low`, `High >= Open`, `High >= Close`, `Low <= Open`, `Low <= Close`, `Volume >= 0`).
  - `deduplicate`: Eliminates duplicate timestamps while preserving the latest authoritative bar.
  - `compute_vwap`: Calculates Volume-Weighted Average Price on every ingested bar series.
  - `detect_missing_gaps`: Analyzes continuous time intervals and flags missing candle gaps based on asset class.
  - `normalize_to_utc`: Ensures all timestamps are UTC-aware.

### 3. Time-Series Caching & Storage Orchestration
- Implemented [`DataCacheService`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/data_pipeline/data_cache.py):
  - Timeframe-aware TTL (30s for 1m bars up to 2h for weekly bars).
- Updated [`MarketDataService`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/services/market_data_service.py):
  - Multi-tier retrieval hierarchy: **Redis Cache → PostgreSQL / SQLite DB → Live Provider Ingestion**.
  - Incremental database candle storage preventing duplicate key conflicts.

### 4. Interactive Frontend Integration (TradingView Charts)
- Built [`LightweightCandleChart`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/charts/LightweightCandleChart.tsx) using TradingView Lightweight Charts v5:
  - Institutional Emerald/Crimson candlestick series + volume histogram overlay.
  - Real-time crosshair inspection and responsive auto-resizing.
- Connected [`AssetDetails.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/AssetDetails.tsx) to live `/api/v1/market/{symbol}/history` and `/quote` endpoints.
- Connected [`MarketExplorer.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/MarketExplorer.tsx) and [`Overview.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/Overview.tsx) to real quotes.

### 5. Automated Verification & Test Coverage
- Pytest suite expanded from 6 to **15 comprehensive tests** (100% passing):
  - `tests/test_validation.py`: OHLC geometric validation, deduplication, VWAP computation, missing gap detection.
  - `tests/test_market_data.py`: Real Yahoo Finance live ingestion, crypto provider normalization, `/history` endpoint, `/quote` endpoint.
- Frontend production build (`tsc -b && vite build`) passed in 3.01s.

---

## 📋 Completed Tasks (Phase 3: AI Financial Sentiment Engine & Technical Indicators)

### 1. Vectorized Technical Analysis Engine in Polars
- Implemented [`TechnicalAnalysisEngine`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/indicators/technical_engine.py):
  - **Moving Averages**: SMA (20, 50, 200) and EMA (12, 26) with recursive alpha decay formulation.
  - **RSI (14)**: Relative Strength Index with average gain/loss rolling window.
  - **MACD**: 12/26 EMA line, 9 EMA signal line, and MACD divergence histogram.
  - **Bollinger Bands**: 20-period middle band with $\pm 2$ standard deviation upper/lower channels.
  - **ATR (14)**: Average True Range measuring true volatility from candle high, low, and prior close.
  - **Stochastic Oscillator**: 14-period %K and 3-period %D lines.
  - **VWAP & Volume MA**: Volume-weighted average price and 20-period volume moving average.
  - **Quantitative Signal Generator (`generate_signals`)**: Emits `BULLISH`, `BEARISH`, or `NEUTRAL` signals with confidence and component breakdown (Golden/Death Cross, RSI overbought/oversold, MACD crossovers, Bollinger breaches).

### 2. FinBERT Financial Sentiment Engine
- Implemented [`FinBERTSentimentEngine`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/sentiment/finbert_engine.py):
  - PyTorch + Hugging Face Transformers loading `ProsusAI/finbert`.
  - Downloads and caches model weights locally (`.cache/huggingface/hub/models--ProsusAI--finbert`).
  - Batch inference support with Softmax probability outputs (`positive_score`, `negative_score`, `neutral_score`).
  - Built-in Loughran-McDonald financial dictionary fallback for zero-latency or offline environments.
  - **Financial Entity Recognition & Relevance**: Automatically extracts target tickers (`NVDA`, `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`, `BTC`, `ETH`) and scores headline relevance.
  - **Market Sentiment Aggregation**: Computes Bullish/Bearish/Neutral Sentiment Indices and market sentiment momentum.

### 3. Live News Ingestion & Correlation Service
- Implemented [`NewsIngestionService`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/sentiment/news_ingestion.py):
  - Ingests real-time financial headlines using Yahoo Finance news feed.
  - SHA-256 deduplication and UTC publication timestamp parsing.
  - Synchronous / asynchronous FinBERT analysis and database persistence.
- Implemented [`SentimentPriceCorrelationService`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/analytics/sentiment_correlation.py):
  - Pearson correlation calculation across multiple configurable time windows (`1h`, `4h`, `24h`, `7d`).
  - Sentiment spike detection ($\ge 2.0\sigma$ standard deviations from rolling mean).
  - Volume spike detection ($\ge 2.0\times$ 20-period average volume).

### 4. REST API Endpoints & UI Integration
- Added endpoints in FastAPI:
  - `GET /api/v1/market/{symbol}/indicators`: Full suite of technical indicators and signal generation.
  - `POST /api/v1/ai/analyze` & `POST /api/v1/ai/analyze/batch`: Live FinBERT inference.
  - `GET /api/v1/ai/sentiment/{symbol}`: Aggregated Bullish/Bearish indices.
  - `GET /api/v1/ai/correlation/{symbol}`: Multi-window Pearson correlation and anomaly spikes.
  - `GET /api/v1/news`, `GET /api/v1/news/sentiment`, `POST /api/v1/news/sync`: Real news stream.
- Updated Frontend:
  - [`AssetDetails.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/AssetDetails.tsx): Displays real calculated technical indicator badges (RSI, MACD, Bollinger Bands, ATR, SMA) and overall technical signal.
  - [`NewsSentiment.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/NewsSentiment.tsx): Interactive FinBERT tester + live news stream with sentiment classification badges.
  - [`AIInsights.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/AIInsights.tsx): Real sentiment correlation metrics across 1h, 4h, 24h, 7d windows with detected sentiment & volume spikes.

### 5. Automated Verification & Test Coverage
- Pytest suite expanded from 15 to **27 comprehensive tests** (100% passing):
  - `tests/test_sentiment.py` (6 tests): FinBERT inference, Loughran-McDonald fallback, entity extraction, sentiment aggregation, `/analyze` and `/correlation` API endpoints.
  - `tests/test_technical_engine.py` (6 tests): SMA, EMA, RSI bounds $[0, 100]$, MACD histogram, Bollinger geometry, ATR positivity, signal generation logic.
- Frontend production build (`tsc -b && vite build`) passed with 0 errors.

---

## 📋 Completed Tasks (Phase 4: Algorithmic Strategy Builder & Event-Driven Backtesting)

### 1. Modular Strategy Architecture & The 7 Quantitative Strategies
- Created [`BaseStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/base.py) abstract interface enforcing strict separation of signal generation from execution.
- Implemented the 7 required quantitative strategies in [`backend/app/strategies/`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/):
  1. [`MovingAverageCrossoverStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/ma_crossover.py): Dual Moving Average Crossover (Fast vs Slow SMA) with crossover event detection.
  2. [`RSIStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/rsi_reversal.py): Mean reversion on oversold ($<30$) and overbought ($>70$) bounds.
  3. [`MACDStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/macd_crossover.py): MACD line & signal line crossover with histogram expansion.
  4. [`BollingerBandsStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/bollinger_reversal.py): Channel reversion from upper/lower $2\sigma$ volatility boundaries.
  5. [`MomentumStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/momentum.py): Rate of Change (ROC) price acceleration breakout model.
  6. [`AISentimentStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/sentiment_strategy.py): Signals driven strictly by high-conviction FinBERT news sentiment spikes with publication timestamps $\le t$.
  7. [`CombinedTechnicalSentimentStrategy`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/combined_strategy.py): Confluence strategy combining RSI momentum with FinBERT institutional sentiment filter.
- Implemented [`STRATEGY_REGISTRY`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/strategies/registry.py) factory to dynamically instantiate strategies by string key.

### 2. Event-Driven Backtesting Engine with Strict Zero Look-Ahead Bias
- Built [`BacktestEngine`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/backtesting/engine.py):
  - **Zero Look-Ahead Bias**: Signal generated on candle $t$ close is queued and filled strictly at candle $t+1$ Open.
  - **Realistic Friction**: Supports configurable commission fees (e.g. 0.1%) and execution price slippage (e.g. 5 bps).
  - **Intraday Risk Controls**: Evaluates intra-candle Stop-Loss and Take-Profit limits against candle High and Low before evaluating new signals.
  - **Portfolio Tracking**: Tracks cash balance, active shares, cost basis, unrealized P&L, mark-to-market equity curve, and round-trip trade logs.

### 3. Institutional Performance Analytics Engine
- Implemented [`PerformanceMetricsCalculator`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/backtesting/metrics.py):
  - **Total Return** and **CAGR** (Compound Annual Growth Rate).
  - **Sharpe Ratio** (excess returns divided by annualized volatility).
  - **Sortino Ratio** (excess returns divided by downside deviation only).
  - **Maximum Drawdown (MDD)** and **Calmar Ratio** ($\text{CAGR} / |\text{MDD}|$).
  - **Win Rate**, **Profit Factor** ($\sum \text{Profits} / \sum \text{Losses}$), Average Winning / Losing Trade.
  - **Exposure Time** (% time capital is deployed).
  - **Buy & Hold Benchmark Comparison**: Measures strategy alpha against holding the underlying asset.

### 4. REST API & Database Persistence
- Implemented endpoints in [`backtests.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/api/v1/endpoints/backtests.py):
  - `POST /api/v1/backtests/run`: Executes full event-driven simulation, saves `BacktestRun` and all `BacktestTrade` records to DB, and returns metrics, equity curve, and trade list.
  - `GET /api/v1/backtests`: Lists past simulation runs ordered by newest first.
  - `GET /api/v1/backtests/{id}`: Returns run details and full metrics.
  - `GET /api/v1/backtests/{id}/trades`: Returns audit log of executed trades.
- Updated [`strategies.py`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/backend/app/api/v1/endpoints/strategies.py) with all 7 prebuilt strategies.

### 5. Frontend Interactive Backtest & Strategy Studio
- Built [`EquityCurveChart`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/charts/EquityCurveChart.tsx): Responsive SVG equity curve with gradient area, Buy & Hold benchmark comparison, and range formatting.
- Upgraded [`Backtesting.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/Backtesting.tsx): Live backtest studio with symbol selector, strategy dropdown, timeframe picker, risk limits (SL/TP), live metrics cards, equity curve, and trade log audit table with P&L badges.
- Upgraded [`StrategyBuilder.tsx`](file:///c:/Users/Dell/Desktop/algorithmic-trading-sentiment-engine/frontend/src/pages/StrategyBuilder.tsx): Modular parameter view for all 7 strategies with direct link to launch backtests.

### 6. Automated Verification & Test Coverage
- Pytest suite expanded from 27 to **34 comprehensive tests** (100% passing):
  - `tests/test_backtest_engine.py` (5 tests):
    - `test_zero_lookahead_bias_guarantee`: Mathematically proves that modifying future data has zero impact on past signals and execution prices.
    - `test_slippage_and_fee_deduction`: Validates fee deduction and price slippage math.
    - `test_stop_loss_trigger`: Validates intra-candle stop-loss fills.
    - `test_performance_metrics_calculator`: Validates Sharpe, Sortino, Drawdown, Profit Factor.
    - `test_all_seven_strategies_execution`: Validates backtest execution across all 7 strategies.
  - `tests/test_backtest_api.py` (2 tests):
    - `test_list_strategies_endpoint`: Verifies prebuilt strategy discovery.
    - `test_run_backtest_api_endpoint`: Verifies end-to-end simulation via REST API and database storage.
- Frontend production build (`tsc -b && vite build`) passed in 2.06s with 0 errors.

---

## 🚀 Next Milestone: Phase 5 (Interactive Institutional Dashboard & Real-Time Analytics)
*Awaiting User Approval to begin Phase 5.*
- Build comprehensive Market Overview (Top Gainers, Losers, Market Sentiment Heatmap).
- Integrate synchronized candlestick + sentiment + indicators multi-pane charts.
- Build Portfolio Simulator with real-time mark-to-market positions and paper-trading execution.
