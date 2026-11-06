import React from 'react';

export const PortfolioSimulator: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-white">Paper Trading & Portfolio Simulator</h1>
        <p className="text-sm text-slate-400">
          Simulate position sizing, margin limits, rebalancing, and live paper execution without financial risk.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Paper Portfolio</span>
          <div className="text-3xl font-black text-white font-mono mt-1">$125,430.50</div>
          <span className="text-xs font-semibold text-emerald-400 font-mono">+25.43% Total Cumulative PnL</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Available Liquid Cash</span>
          <div className="text-3xl font-black text-white font-mono mt-1">$45,200.00</div>
          <span className="text-xs text-slate-500 font-mono">36.03% Cash Allocation</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Unrealized Open PnL</span>
          <div className="text-3xl font-black text-emerald-400 font-mono mt-1">+$4,230.50</div>
          <span className="text-xs text-emerald-400 font-mono">+3.48% on active positions</span>
        </div>
      </div>
    </div>
  );
};
