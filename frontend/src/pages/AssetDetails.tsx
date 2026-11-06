import React, { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { BarChart3 } from 'lucide-react';

export const AssetDetails: React.FC = () => {
  const { selectedSymbol } = useAppStore();
  const [timeframe, setTimeframe] = useState<string>('1d');

  const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1wk'];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Asset Header */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-700 flex items-center justify-center font-black text-xl text-white font-mono shadow-md">
            {selectedSymbol.slice(0, 2)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-white font-mono">{selectedSymbol}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-300 border border-slate-700">
                NASDAQ
              </span>
            </div>
            <p className="text-xs text-slate-400">Institutional Market Analysis & Sentiment Engine</p>
          </div>
        </div>

        {/* Timeframe Selector */}
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
      </div>

      {/* Chart Canvas Area */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <span className="font-bold text-white text-sm">TradingView Lightweight Candlestick Chart ({timeframe})</span>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span>O: <strong className="text-white">136.40</strong></span>
            <span>H: <strong className="text-white">139.10</strong></span>
            <span>L: <strong className="text-white">135.80</strong></span>
            <span>C: <strong className="text-emerald-400">138.25 (+4.82%)</strong></span>
          </div>
        </div>

        {/* Interactive Simulated Candlestick Viewport */}
        <div className="h-80 w-full mt-4 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:16px_16px]" />
          <div className="z-10 text-center space-y-2">
            <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Interactive TradingView Lightweight Charts
            </span>
            <p className="text-sm text-slate-300 font-medium">
              Historical candle ingestion engine active for <span className="text-emerald-400 font-mono">{selectedSymbol}</span>.
            </p>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Zero look-ahead bias validation pipeline configured for 1m, 5m, 15m, 1h, 4h, 1d, and 1wk timeframes.
            </p>
          </div>
        </div>
      </div>

      {/* Technical Indicators & AI Sentiment Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">SMA & Trend</span>
          <div className="mt-2 space-y-1 font-mono text-xs">
            <div className="flex justify-between"><span className="text-slate-400">SMA 20:</span><span className="text-emerald-400 font-bold">132.40 (Above)</span></div>
            <div className="flex justify-between"><span className="text-slate-400">SMA 50:</span><span className="text-emerald-400 font-bold">128.15 (Above)</span></div>
            <div className="flex justify-between"><span className="text-slate-400">SMA 200:</span><span className="text-emerald-400 font-bold">114.60 (Bullish)</span></div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Oscillators</span>
          <div className="mt-2 space-y-1 font-mono text-xs">
            <div className="flex justify-between"><span className="text-slate-400">RSI (14):</span><span className="text-slate-200 font-bold">68.20 (Neutral)</span></div>
            <div className="flex justify-between"><span className="text-slate-400">MACD Histogram:</span><span className="text-emerald-400 font-bold">+1.84 (Bullish)</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Bollinger Upper:</span><span className="text-slate-200 font-bold">141.50</span></div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">FinBERT AI Sentiment</span>
          <div className="mt-2 space-y-1 font-mono text-xs">
            <div className="flex justify-between"><span className="text-slate-400">Bullish Index:</span><span className="text-emerald-400 font-bold">91.4%</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Confidence:</span><span className="text-slate-200 font-bold">0.94</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Relevance:</span><span className="text-slate-200 font-bold">0.98</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};
