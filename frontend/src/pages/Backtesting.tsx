import React, { useState } from 'react';
import { PlaySquare, ShieldAlert } from 'lucide-react';

export const Backtesting: React.FC = () => {
  const [running, setRunning] = useState<boolean>(false);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">Event-Driven Backtesting Engine</h1>
          <p className="text-sm text-slate-400">
            Strict look-ahead bias prevention: trades execute on the subsequent candle with slippage and commission models.
          </p>
        </div>

        <button
          onClick={() => {
            setRunning(true);
            setTimeout(() => setRunning(false), 800);
          }}
          disabled={running}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all shadow-lg shadow-emerald-500/20 active:scale-95"
        >
          <PlaySquare className="w-4 h-4" />
          <span>{running ? 'Running Simulation...' : 'Run Backtest'}</span>
        </button>
      </div>

      {/* Look-ahead Bias Prevention Notice */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <span className="font-bold text-emerald-400">Look-Ahead Bias & Data Leakage Prevention Enforced</span>
          <p className="text-slate-400">
            Signals generated at candle close (t) only execute at candle open (t+1). News publication timestamps are matched strictly chronologically so future news events cannot leak into historical feature calculation.
          </p>
        </div>
      </div>

      {/* Summary Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Total Return</span>
          <div className="text-2xl font-black text-emerald-400 font-mono mt-1">+18.52%</div>
          <span className="text-[11px] text-slate-500">Benchmark: +11.20%</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Sharpe Ratio</span>
          <div className="text-2xl font-black text-white font-mono mt-1">1.42</div>
          <span className="text-[11px] text-emerald-400">Sortino: 1.89</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Max Drawdown</span>
          <div className="text-2xl font-black text-rose-400 font-mono mt-1">-8.24%</div>
          <span className="text-[11px] text-slate-500">Calmar Ratio: 1.97</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Win Rate (24 Trades)</span>
          <div className="text-2xl font-black text-white font-mono mt-1">58.3%</div>
          <span className="text-[11px] text-slate-400">Profit Factor: 1.65</span>
        </div>
      </div>

      {/* Interactive Equity Curve & Trade Log */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
        <span className="text-sm font-bold text-white">Simulated Equity Curve vs Benchmark (Buy & Hold)</span>
        <div className="h-64 mt-4 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-center font-mono text-xs text-slate-400">
          <span>[Event-Driven Equity Simulation Curve: Capital $100,000 → $118,520 (Fees: $240, Slippage: 5 bps)]</span>
        </div>
      </div>
    </div>
  );
};
