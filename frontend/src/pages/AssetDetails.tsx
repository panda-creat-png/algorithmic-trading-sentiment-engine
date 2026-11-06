import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '../store/useAppStore';
import { api } from '../services/api';
import { LightweightCandleChart } from '../charts/LightweightCandleChart';
import {
  BarChart3,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Sliders,
  TrendingUp,
} from 'lucide-react';

export const AssetDetails: React.FC = () => {
  const { selectedSymbol } = useAppStore();
  const [timeframe, setTimeframe] = useState<string>('1d');

  const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1wk'];

  // Fetch real OHLCV historical candles
  const {
    data: historyData,
    refetch: refetchHistory,
    isFetching: historyFetching,
  } = useQuery({
    queryKey: ['market-history', selectedSymbol, timeframe],
    queryFn: () => api.getMarketHistory(selectedSymbol, timeframe, 120),
    staleTime: 30000,
  });

  // Fetch real-time live quote
  const { data: quoteData } = useQuery({
    queryKey: ['market-quote', selectedSymbol],
    queryFn: () => api.getQuote(selectedSymbol),
    refetchInterval: 10000,
  });

  // Fetch computed technical indicators & quantitative signals
  const { data: indicatorData, refetch: refetchIndicators } = useQuery({
    queryKey: ['technical-indicators', selectedSymbol, timeframe],
    queryFn: () => api.getTechnicalIndicators(selectedSymbol, timeframe, 60),
    staleTime: 30000,
  });

  const candles = historyData?.candles || [];
  const latestCandle = candles.length > 0 ? candles[candles.length - 1] : null;

  const isPositive = (quoteData?.change ?? 0) >= 0;

  const metrics = indicatorData?.latest_metrics || {};
  const signals = indicatorData?.signals || [];
  const bias = indicatorData?.bias || 'BULLISH';

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Asset Header */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-700 flex items-center justify-center font-black text-xl text-white font-mono shadow-md">
            {selectedSymbol.slice(0, 2)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-white font-mono">{selectedSymbol}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-300 border border-slate-700">
                {selectedSymbol.includes('-USD') ? 'CRYPTO 24/7' : 'US EQUITY'}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                  bias === 'BULLISH'
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : bias === 'BEARISH'
                    ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                    : 'bg-slate-800 text-slate-300 border-slate-700'
                }`}
              >
                BIAS: {bias}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xl font-black text-white font-mono">
                ${(quoteData?.price ?? latestCandle?.close ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
              {quoteData && (
                <span className={`flex items-center text-xs font-bold ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {isPositive ? <ArrowUpRight className="w-4 h-4 mr-0.5" /> : <ArrowDownRight className="w-4 h-4 mr-0.5" />}
                  {isPositive ? `+${quoteData.change}` : quoteData.change} ({quoteData.change_percent}%)
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Timeframe Selector & Actions */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all ${
                  timeframe === tf ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          <button
            onClick={() => {
              refetchHistory();
              refetchIndicators();
            }}
            disabled={historyFetching}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh candles & indicators"
          >
            <RefreshCw className={`w-4 h-4 ${historyFetching ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* TradingView Lightweight Charts Viewport */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <span className="font-bold text-white text-sm">
              TradingView Lightweight Candlestick Chart ({selectedSymbol} • {timeframe})
            </span>
            <span className="text-xs text-slate-500">
              ({candles.length} candles ingested)
            </span>
          </div>

          {latestCandle && (
            <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-slate-400">
              <span>O: <strong className="text-slate-200">{latestCandle.open.toFixed(2)}</strong></span>
              <span>H: <strong className="text-slate-200">{latestCandle.high.toFixed(2)}</strong></span>
              <span>L: <strong className="text-slate-200">{latestCandle.low.toFixed(2)}</strong></span>
              <span>C: <strong className="text-emerald-400">{latestCandle.close.toFixed(2)}</strong></span>
              <span>Vol: <strong className="text-slate-200">{latestCandle.volume.toLocaleString()}</strong></span>
              {latestCandle.vwap && (
                <span>VWAP: <strong className="text-cyan-400">{latestCandle.vwap.toFixed(2)}</strong></span>
              )}
            </div>
          )}
        </div>

        {/* Real Candlestick Canvas */}
        <div className="mt-4">
          <LightweightCandleChart
            candles={candles}
            symbol={selectedSymbol}
            timeframe={timeframe}
          />
        </div>
      </div>

      {/* Real Computed Technical Indicators Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Box 1: Trend Indicators */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            <span>Trend & Moving Averages</span>
            <Sliders className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="mt-2 space-y-1.5 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">SMA 20:</span>
              <span className="text-slate-200 font-bold">${metrics.sma_20 ? metrics.sma_20.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">SMA 50:</span>
              <span className="text-slate-200 font-bold">${metrics.sma_50 ? metrics.sma_50.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">VWAP:</span>
              <span className="text-cyan-400 font-bold">${latestCandle?.vwap ? latestCandle.vwap.toFixed(2) : '--'}</span>
            </div>
          </div>
        </div>

        {/* Box 2: Momentum & Volatility */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            <span>Momentum & Volatility</span>
            <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="mt-2 space-y-1.5 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">RSI (14):</span>
              <span className={`font-bold ${metrics.rsi_14 > 70 ? 'text-rose-400' : metrics.rsi_14 < 30 ? 'text-emerald-400' : 'text-slate-200'}`}>
                {metrics.rsi_14 ? metrics.rsi_14.toFixed(2) : '50.00'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">MACD Line:</span>
              <span className="text-slate-200 font-bold">{metrics.macd_line ? metrics.macd_line.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">ATR (14):</span>
              <span className="text-slate-200 font-bold">${metrics.atr_14 ? metrics.atr_14.toFixed(2) : '--'}</span>
            </div>
          </div>
        </div>

        {/* Box 3: Bollinger & Signals */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            <span>Quantitative Signals</span>
            <Zap className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="mt-2 space-y-1 text-xs">
            {signals.length > 0 ? (
              signals.map((sig: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between py-1 border-b border-slate-800/60 font-mono">
                  <span className="text-slate-300 font-bold">{sig.type}</span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      sig.signal.includes('BULLISH')
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-rose-500/20 text-rose-400'
                    }`}
                  >
                    {sig.signal}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-slate-500 py-3 text-center">No active breakout thresholds triggered.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
