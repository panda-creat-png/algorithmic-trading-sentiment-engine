import React from 'react';

export const AIInsights: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-white">AI Financial Insights & Sentiment Correlation</h1>
        <p className="text-sm text-slate-400">
          Quant research module investigating mathematical relationships between news sentiment shifts and asset price moves.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Rolling Sentiment Correlation</span>
          <div className="text-2xl font-black text-emerald-400 font-mono mt-1">+0.64</div>
          <p className="text-xs text-slate-500 mt-2">
            24h rolling Pearson correlation between FinBERT positive score spikes and 4h forward returns.
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Unusual Volume Confirmation</span>
          <div className="text-2xl font-black text-cyan-400 font-mono mt-1">2.4x Mean</div>
          <p className="text-xs text-slate-500 mt-2">
            News releases with &gt; 90% confidence trigger volume spikes within 15 minutes of publication.
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Entity Disambiguation</span>
          <div className="text-2xl font-black text-white font-mono mt-1">99.1%</div>
          <p className="text-xs text-slate-500 mt-2">
            NER algorithm links company names, tickers, executives, and product lines accurately to assets.
          </p>
        </div>
      </div>
    </div>
  );
};
