# QuantMind AI 🧠📈

**QuantMind AI** is an institutional-grade algorithmic trading research, backtesting, and AI-powered sentiment intelligence web platform. It unifies financial market data processing (OHLCV), natural language processing via FinBERT sentiment modeling, multi-strategy backtesting without look-ahead bias, and interactive financial dashboards.

> **IMPORTANT**: QuantMind AI is strictly an institutional research and paper-trading platform. It executes simulated paper trades only and never issues guaranteed profit forecasts or executes real financial transactions.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2 (Async), PostgreSQL / TimescaleDB, Redis, Polars, Pydantic v2.
- **AI & NLP**: Hugging Face Transformers, FinBERT (`ProsusAI/finbert`), PyTorch, Scikit-Learn.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, TanStack React Query, TradingView Lightweight Charts, Lucide Icons.
- **DevOps**: Docker, Docker Compose, Nginx, Pytest.

---

## 🏗️ Architecture Overview

```
quantmind-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/  # Health, Market, News, AI, Strategies, Backtests, Portfolio
│   │   ├── core/              # Config, Async DB, Redis client, Security, Logging
│   │   ├── models/            # SQLAlchemy 2 Declarative ORM models (12 tables)
│   │   ├── schemas/           # Pydantic v2 validation models
│   │   ├── services/          # Cache & Market Data services
│   │   ├── data_pipeline/     # Ingestion & Polars processing (Phase 2)
│   │   ├── sentiment/         # FinBERT inference & aggregation (Phase 3)
│   │   ├── backtesting/       # Event-driven backtesting engine (Phase 4)
│   │   └── main.py            # FastAPI ASGI application entrypoint
│   ├── tests/                 # Automated Pytest suite
│   ├── Dockerfile             # Python 3.12 container specification
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # Sidebar, TopNavbar, shared UI widgets
│   │   ├── pages/             # 10 Institutional dashboard views
│   │   ├── layouts/           # MainLayout container
│   │   ├── store/             # Zustand state management
│   │   ├── services/          # Axios typed API client
│   │   └── hooks/             # React Query hooks (health polling)
│   ├── Dockerfile             # Multi-stage Node + Nginx container
│   └── package.json           # Frontend dependencies (React 19, Tailwind)
├── docker-compose.yml         # Multi-container orchestration (PostgreSQL, Redis, App)
├── DEVELOPMENT.md             # Implementation tracking and roadmap
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.12+ (Python 3.13 verified)
- Node.js 20+ (Node 22 verified)
- Optional: Docker & Docker Compose or local Redis & PostgreSQL

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m pytest -v
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/api/v1/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend interface will be live at: `http://localhost:5173`

### 4. Running with Docker Compose
```bash
docker compose up --build
```
- Frontend: `http://localhost:80`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## 🔒 Security & Data Integrity Principles
1. **Zero Look-Ahead Bias**: Signals at candle close $t$ execute exclusively on candle open $t+1$. Historical news publication timestamps are matched strictly chronologically.
2. **Transparent Fallbacks**: Redis caching falls back cleanly to in-memory TTL dictionary caching if Redis is offline during local development.
3. **Institutional UI**: Bloomberg/TradingView-inspired dark mode theme with real-time connection status pills.

---

## 📄 License
MIT License. Created for quantitative research and educational simulation.

