import React from 'react';

export const PerformanceAnalytics: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-white">Performance Analytics & Risk Attribution</h1>
        <p className="text-sm text-slate-400">
          Monthly returns heatmaps, drawdown duration analysis, Sortino ratios, and Sharpe decomposition.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Annualized Return (CAGR)</span>
          <div className="text-2xl font-black text-emerald-400 font-mono mt-1">+16.24%</div>
        </div>
        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Annualized Volatility</span>
          <div className="text-2xl font-black text-white font-mono mt-1">14.12%</div>
        </div>
        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Profit Factor</span>
          <div className="text-2xl font-black text-white font-mono mt-1">1.65</div>
        </div>
        <div className="p-4 rounded-xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Market Exposure Time</span>
          <div className="text-2xl font-black text-white font-mono mt-1">62.4%</div>
        </div>
      </div>
    </div>
  );
};
