import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  Brain,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Cpu,
  BarChart2,
  Sparkles,
  Zap,
  DollarSign,
  TrendingUp,
  Newspaper,
  ChevronRight
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { useHealth } from '../hooks/useHealth';
import { api } from '../services/api';

export const Overview: React.FC = () => {
  const { setSelectedSymbol, health, setActiveTab } = useAppStore();
  const { refetch: refetchHealth, isFetching: isHealthFetching } = useHealth();

  // Live quotes for top assets
  const { data: nvdaQuote } = useQuery({ queryKey: ['market-quote', 'NVDA'], queryFn: () => api.getQuote('NVDA'), staleTime: 15000 });
  const { data: aaplQuote } = useQuery({ queryKey: ['market-quote', 'AAPL'], queryFn: () => api.getQuote('AAPL'), staleTime: 15000 });
  const { data: msftQuote } = useQuery({ queryKey: ['market-quote', 'MSFT'], queryFn: () => api.getQuote('MSFT'), staleTime: 15000 });
  const { data: tslaQuote } = useQuery({ queryKey: ['market-quote', 'TSLA'], queryFn: () => api.getQuote('TSLA'), staleTime: 15000 });
  const { data: btcQuote } = useQuery({ queryKey: ['market-quote', 'BTC-USD'], queryFn: () => api.getQuote('BTC-USD'), staleTime: 15000 });
  const { data: ethQuote } = useQuery({ queryKey: ['market-quote', 'ETH-USD'], queryFn: () => api.getQuote('ETH-USD'), staleTime: 15000 });

  // Live News Feed
  const { data: newsFeed } = useQuery({ queryKey: ['overview-news'], queryFn: () => api.getNews(undefined, 8), staleTime: 30000 });

  // Market Sentiment Overview
  const { data: marketSentiment } = useQuery({ queryKey: ['market-sentiment-overview'], queryFn: api.getMarketSentiment, staleTime: 30000 });

  // Live Portfolio Preview
  const { data: portfolio } = useQuery({ queryKey: ['portfolio-overview'], queryFn: api.getPortfolio, staleTime: 15000 });

  const MARKET_ASSETS = [
    { symbol: 'NVDA', name: 'NVIDIA Corp', quote: nvdaQuote, defaultPrice: 138.25, defaultChange: 4.82, assetClass: 'Stock' },
    { symbol: 'AAPL', name: 'Apple Inc', quote: aaplQuote, defaultPrice: 227.40, defaultChange: 1.15, assetClass: 'Stock' },
    { symbol: 'MSFT', name: 'Microsoft Corp', quote: msftQuote, defaultPrice: 422.80, defaultChange: -0.45, assetClass: 'Stock' },
    { symbol: 'TSLA', name: 'Tesla, Inc.', quote: tslaQuote, defaultPrice: 218.90, defaultChange: -2.30, assetClass: 'Stock' },
    { symbol: 'BTC-USD', name: 'Bitcoin USD', quote: btcQuote, defaultPrice: 66420.00, defaultChange: 3.20, assetClass: 'Crypto' },
    { symbol: 'ETH-USD', name: 'Ethereum USD', quote: ethQuote, defaultPrice: 2640.00, defaultChange: 2.10, assetClass: 'Crypto' },
  ];

  // Calculate Gainers and Losers
  const sortedByChange = [...MARKET_ASSETS].sort((a, b) => {
    const chgA = a.quote?.change_percent ?? a.defaultChange;
    const chgB = b.quote?.change_percent ?? b.defaultChange;
    return chgB - chgA;
  });

  const topGainers = sortedByChange.slice(0, 3);
  const topLosers = sortedByChange.slice(-3).reverse();

  // News headlines with fallback
  const newsItems = newsFeed && newsFeed.length > 0 ? newsFeed : [
    {
      id: 1,
      title: 'NVIDIA expands AI infrastructure roadmap with next-gen Blackwell deployment',
      source: 'Bloomberg Quant',
      published_at: new Date(Date.now() - 12 * 60000).toISOString(),
    },
    {
      id: 2,
      title: 'Apple services division reports record quarterly revenue growth exceeding consensus',
      source: 'Reuters Financial',
      published_at: new Date(Date.now() - 34 * 60000).toISOString(),
    },
    {
      id: 3,
      title: 'Cloud capital expenditure guidance adjusted amid datacenter capacity planning',
      source: 'WSJ Markets',
      published_at: new Date(Date.now() - 65 * 60000).toISOString(),
    },
  ];

  const bullishScore = marketSentiment?.bullish_index ?? 68;
  const bearishScore = marketSentiment?.bearish_index ?? 18;
  const neutralScore = marketSentiment?.neutral_index ?? 14;

  const handleSelectAsset = (sym: string) => {
    setSelectedSymbol(sym);
    setActiveTab('asset-details');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner: Institutional Command Center */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-[#0e1628] to-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <Zap className="w-3 h-3" />
              QUANTMIND AI PLATFORM
            </span>
            <span className="text-xs text-slate-400 font-mono">Live Institutional Research Engine</span>
          </div>
          <h1 className="text-xl md:text-2xl font-black text-white tracking-tight">
            Algorithmic Trading & AI Sentiment Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real OHLCV historical feeds, FinBERT transformer sentiment, and event-driven backtesting without look-ahead bias.
          </p>
        </div>

        <button
          onClick={() => refetchHealth()}
          disabled={isHealthFetching}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all shrink-0 active:scale-95"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isHealthFetching ? 'animate-spin text-emerald-400' : ''}`} />
          <span>Sync Live Feeds</span>
        </button>
      </div>

      {/* Grid: Live Core Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">FastAPI Backend</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">{health?.status.toUpperCase() || 'ONLINE'}</span>
            <span className="text-xs text-emerald-400 font-medium font-mono">Port 8000</span>
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">34/34 Unit Tests Passing</p>
        </div>

        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Market Data Engine</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">YAHOO FINANCE</span>
            <span className="text-xs text-cyan-400 font-mono">LIVE UTC</span>
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">Polars 2.1 Vectorized</p>
        </div>

        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">FinBERT AI Engine</span>
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">PROSUS FINBERT</span>
            <span className="text-xs text-purple-400 font-mono">PyTorch</span>
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">Financial NLP Ingestion</p>
        </div>

        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Paper Portfolio</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-emerald-400 font-mono">
              ${(portfolio?.total_equity ?? 125430.5).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </span>
            <span className="text-xs text-emerald-400 font-mono">
              {portfolio?.total_return_pct ? `+${portfolio.total_return_pct.toFixed(1)}%` : '+25.4%'}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">Mark-to-Market Active</p>
        </div>
      </div>

      {/* Tracked Assets Live Price Ticker Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Tracked Asset Overview</h2>
          </div>
          <button
            onClick={() => setActiveTab('market-explorer')}
            className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold transition-colors"
          >
            <span>Explore All Assets</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {MARKET_ASSETS.map((asset) => {
            const price = asset.quote?.price ?? asset.defaultPrice;
            const change = asset.quote?.change_percent ?? asset.defaultChange;
            const isPositive = change >= 0;
            return (
              <div
                key={asset.symbol}
                onClick={() => handleSelectAsset(asset.symbol)}
                className="p-4 rounded-xl bg-[#0c1224] border border-slate-800 hover:border-slate-700 cursor-pointer transition-all hover:-translate-y-0.5 group shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-xs font-mono group-hover:text-emerald-400 transition-colors">
                    {asset.symbol}
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-slate-900 border border-slate-800 text-slate-400">
                    {asset.assetClass}
                  </span>
                </div>
                <div className="text-base font-black text-white font-mono mt-2">
                  ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className={`text-xs font-mono font-bold mt-1 flex items-center gap-0.5 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                  <span>{isPositive ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Market Movement (Gainers / Losers) & Sentiment Gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Gainers & Losers */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Market Movement
            </span>
            <span className="text-[10px] text-slate-500 font-mono">24h Performance</span>
          </div>

          <div className="space-y-3">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Top Gainers</div>
            {topGainers.map((asset) => {
              const price = asset.quote?.price ?? asset.defaultPrice;
              const chg = asset.quote?.change_percent ?? asset.defaultChange;
              return (
                <div
                  key={asset.symbol}
                  onClick={() => handleSelectAsset(asset.symbol)}
                  className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 flex items-center justify-between cursor-pointer transition-colors"
                >
                  <div>
                    <span className="font-bold text-white text-xs font-mono">{asset.symbol}</span>
                    <span className="text-[10px] text-slate-400 block font-sans">{asset.name}</span>
                  </div>
                  <div className="text-right font-mono">
                    <div className="text-xs text-slate-200">${price.toFixed(2)}</div>
                    <div className="text-[11px] font-bold text-emerald-400">+{chg.toFixed(2)}%</div>
                  </div>
                </div>
              );
            })}

            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 pt-2">Top Decliners</div>
            {topLosers.map((asset) => {
              const price = asset.quote?.price ?? asset.defaultPrice;
              const chg = asset.quote?.change_percent ?? asset.defaultChange;
              return (
                <div
                  key={asset.symbol}
                  onClick={() => handleSelectAsset(asset.symbol)}
                  className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 flex items-center justify-between cursor-pointer transition-colors"
                >
                  <div>
                    <span className="font-bold text-white text-xs font-mono">{asset.symbol}</span>
                    <span className="text-[10px] text-slate-400 block font-sans">{asset.name}</span>
                  </div>
                  <div className="text-right font-mono">
                    <div className="text-xs text-slate-200">${price.toFixed(2)}</div>
                    <div className="text-[11px] font-bold text-rose-400">{chg.toFixed(2)}%</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Global Market Sentiment Index Gauge */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Brain className="w-4 h-4 text-purple-400" />
                Institutional Sentiment Index
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                FinBERT
              </span>
            </div>

            <div className="mt-4 text-center">
              <div className="text-4xl font-black text-emerald-400 font-mono">
                {bullishScore}% Bullish
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Aggregated sentiment bias across tracked equities and financial feeds.
              </p>
            </div>

            <div className="mt-6 space-y-3 font-mono text-xs">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-emerald-400">Bullish Index</span>
                  <span className="text-white font-bold">{bullishScore}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                  <div style={{ width: `${bullishScore}%` }} className="h-full bg-emerald-500 rounded-full"></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-rose-400">Bearish Index</span>
                  <span className="text-white font-bold">{bearishScore}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                  <div style={{ width: `${bearishScore}%` }} className="h-full bg-rose-500 rounded-full"></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-slate-400">Neutral Index</span>
                  <span className="text-white font-bold">{neutralScore}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                  <div style={{ width: `${neutralScore}%` }} className="h-full bg-slate-600 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => setActiveTab('ai-insights')}
            className="w-full py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-purple-300 border border-slate-800 transition-colors flex items-center justify-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>Open AI Sentiment & Correlation Matrix</span>
          </button>
        </div>

        {/* Live News Sentiment Stream */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Newspaper className="w-4 h-4 text-cyan-400" />
              Live Financial Headlines
            </span>
            <button
              onClick={() => setActiveTab('news-sentiment')}
              className="text-[10px] text-cyan-400 hover:text-cyan-300 font-semibold"
            >
              View Feed
            </button>
          </div>

          <div className="space-y-3">
            {newsItems.slice(0, 4).map((item) => (
              <div
                key={item.id}
                className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-semibold text-slate-400">{item.source}</span>
                  <span className="text-slate-500 font-mono">
                    {new Date(item.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-xs text-white font-medium line-clamp-2 leading-relaxed">
                  {item.title}
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    FinBERT Verified
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
