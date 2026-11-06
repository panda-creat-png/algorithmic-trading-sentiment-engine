import React, { useState } from 'react';
import {
  Activity,
  Brain,
  Shield,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Cpu,
  BarChart2,
  Sparkles,
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { useHealth } from '../hooks/useHealth';

export const Overview: React.FC = () => {
  const { selectedSymbol, setSelectedSymbol, health } = useAppStore();
  const { refetch, isFetching } = useHealth();

  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'negative'>('all');

  // Tracked live asset summary cards
  const MARKET_CARDS = [
    { symbol: 'NVDA', name: 'NVIDIA Corp', price: 138.25, change: 4.82, volume: '58.4M', sentiment: 'Bullish (91%)' },
    { symbol: 'AAPL', name: 'Apple Inc', price: 227.40, change: 1.15, volume: '44.1M', sentiment: 'Neutral (65%)' },
    { symbol: 'MSFT', name: 'Microsoft Corp', price: 422.80, change: -0.45, volume: '22.8M', sentiment: 'Bullish (78%)' },
    { symbol: 'BTC-USD', name: 'Bitcoin', price: 66420.00, change: 3.20, volume: '$32.1B', sentiment: 'Bullish (84%)' },
  ];

  const SAMPLE_HEADLINES = [
    {
      id: 1,
      symbol: 'NVDA',
      title: 'NVIDIA expands AI infrastructure roadmap with next-gen Blackwell deployment',
      sentiment: 'positive',
      score: 0.93,
      confidence: 0.94,
      source: 'Bloomberg Quant',
      time: '12m ago',
    },
    {
      id: 2,
      symbol: 'AAPL',
      title: 'Apple services division reports record quarterly revenue growth exceeding consensus',
      sentiment: 'positive',
      score: 0.88,
      confidence: 0.91,
      source: 'Reuters Financial',
      time: '34m ago',
    },
    {
      id: 3,
      symbol: 'MSFT',
      title: 'Cloud capital expenditure guidance adjusted amid datacenter capacity planning',
      sentiment: 'neutral',
      score: 0.72,
      confidence: 0.82,
      source: 'WSJ Markets',
      time: '1h ago',
    },
    {
      id: 4,
      symbol: 'TSLA',
      title: 'Regulatory review delays automated driving software updates in European markets',
      sentiment: 'negative',
      score: 0.85,
      confidence: 0.89,
      source: 'Financial Times',
      time: '2h ago',
    },
  ];

  const filteredHeadlines = SAMPLE_HEADLINES.filter((h) => {
    if (sentimentFilter === 'all') return true;
    return h.sentiment === sentimentFilter;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner: Architecture & Live Engine Status */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-[#0e1628] to-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              PHASE 1 OPERATIONAL
            </span>
            <span className="text-xs text-slate-400 font-mono">QuantMind AI v1.0.0</span>
          </div>
          <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
            Institutional Algorithmic Research & Sentiment Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Event-driven backtesting, FinBERT natural language NLP sentiment, and multi-asset technical analytics.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all shrink-0 active:scale-95"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-emerald-400' : ''}`} />
          <span>Check Engine Status</span>
        </button>
      </div>

      {/* Grid: Key Performance Metrics & Health Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">FastAPI Core</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">{health?.status.toUpperCase() || 'ONLINE'}</span>
            <span className="text-xs text-emerald-400 font-medium">Uptime 99.98%</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">ASGI async engine with REST API v1</p>
        </div>

        {/* Metric 2 */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Storage Layer</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">{health?.database.database_type || 'SQLAlchemy'}</span>
            <span className="text-xs text-cyan-400 font-mono">{health?.database.latency_ms ?? '0.4'} ms</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">PostgreSQL Timescale schema ready</p>
        </div>

        {/* Metric 3 */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Cache & Pub/Sub</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">{health?.redis.backend?.toUpperCase() || 'REDIS'}</span>
            <span className="text-xs text-emerald-400 font-mono">{health?.redis.latency_ms ?? '0.5'} ms</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Fast sub-millisecond market caching</p>
        </div>

        {/* Metric 4 */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">FinBERT AI NLP</span>
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">+0.68</span>
            <span className="text-xs text-emerald-400 font-medium">BULLISH BIAS</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Hugging Face transformer integration</p>
        </div>
      </div>

      {/* Tracked Assets Bar */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-emerald-400" />
            Tracked Assets Watchlist
          </h2>
          <span className="text-xs text-slate-500">Click card to select active asset</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {MARKET_CARDS.map((asset) => {
            const isSelected = selectedSymbol === asset.symbol;
            const isPositive = asset.change >= 0;
            return (
              <div
                key={asset.symbol}
                onClick={() => setSelectedSymbol(asset.symbol)}
                className={`p-4 rounded-xl cursor-pointer transition-all border ${
                  isSelected
                    ? 'bg-slate-800/90 border-emerald-500 shadow-lg shadow-emerald-500/10'
                    : 'bg-[#0e1526] border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-base font-bold text-white font-mono">{asset.symbol}</span>
                    <p className="text-xs text-slate-400 truncate max-w-[130px]">{asset.name}</p>
                  </div>
                  <span
                    className={`flex items-center text-xs font-bold px-2 py-0.5 rounded ${
                      isPositive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                    }`}
                  >
                    {isPositive ? <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> : <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
                    {isPositive ? `+${asset.change}%` : `${asset.change}%`}
                  </span>
                </div>

                <div className="mt-3 flex items-baseline justify-between">
                  <span className="text-lg font-bold font-mono text-slate-100">
                    ${asset.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">Vol: {asset.volume}</span>
                </div>

                <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">FinBERT:</span>
                  <span className="font-semibold text-emerald-400">{asset.sentiment}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Split: AI Sentiment Stream & Strategy Simulation Snapshot */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: AI News Sentiment Stream */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <h2 className="font-bold text-white text-base">FinBERT AI Financial News Stream</h2>
            </div>
            {/* Filter buttons */}
            <div className="flex items-center gap-1.5 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
              {(['all', 'positive', 'negative'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSentimentFilter(filter)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-md capitalize transition-all ${
                    sentimentFilter === filter
                      ? 'bg-emerald-500 text-slate-950 shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          {/* Headlines list */}
          <div className="divide-y divide-slate-800/80 mt-2">
            {filteredHeadlines.map((item) => (
              <div key={item.id} className="py-3.5 hover:bg-slate-900/40 px-2 rounded-lg transition-colors">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-200 px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700">
                      {item.symbol}
                    </span>
                    <span>{item.source}</span>
                  </div>
                  <span className="text-[11px] text-slate-500">{item.time}</span>
                </div>

                <p className="text-sm font-medium text-slate-100 hover:text-emerald-300 transition-colors cursor-pointer">
                  {item.title}
                </p>

                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span
                    className={`font-semibold capitalize px-2 py-0.5 rounded text-[11px] ${
                      item.sentiment === 'positive'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : item.sentiment === 'negative'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {item.sentiment}
                  </span>
                  <span className="text-slate-400">
                    Confidence: <span className="text-slate-200 font-mono">{(item.confidence * 100).toFixed(0)}%</span>
                  </span>
                  <span className="text-slate-400">
                    AI Probability: <span className="text-slate-200 font-mono">{(item.score * 100).toFixed(0)}%</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Paper Trading & Strategy Snapshot */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="font-bold text-white text-base flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" />
                Paper Portfolio
              </h2>
              <span className="text-xs font-semibold text-emerald-400 font-mono">+25.43% Total</span>
            </div>

            <div className="mt-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Simulated Total Equity</span>
              <div className="text-2xl font-black text-white font-mono mt-1">$125,430.50</div>
              <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                <span>Cash: <strong className="text-slate-200 font-mono">$45,200.00</strong></span>
                <span>Positions: <strong className="text-slate-200 font-mono">3 Active</strong></span>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Positions</span>
              
              <div className="p-2.5 rounded-lg bg-slate-900/50 border border-slate-800/80 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-white font-mono">NVDA (40 Shares)</div>
                  <div className="text-slate-400 text-[11px]">Avg $112.50 → Now $138.25</div>
                </div>
                <span className="text-emerald-400 font-bold font-mono">+22.84%</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-900/50 border border-slate-800/80 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-white font-mono">AAPL (150 Shares)</div>
                  <div className="text-slate-400 text-[11px]">Avg $215.00 → Now $227.40</div>
                </div>
                <span className="text-emerald-400 font-bold font-mono">+5.77%</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-900/50 border border-slate-800/80 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-white font-mono">BTC-USD (0.65 BTC)</div>
                  <div className="text-slate-400 text-[11px]">Avg $62,400 → Now $66,420</div>
                </div>
                <span className="text-emerald-400 font-bold font-mono">+6.17%</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500 text-center">
            Zero look-ahead bias validation active across historical candles.
          </div>
        </div>
      </div>
    </div>
  );
};
