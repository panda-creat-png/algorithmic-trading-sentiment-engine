import React from 'react';
import { Server } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export const Settings: React.FC = () => {
  const { health } = useAppStore();

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-white">System Settings & API Configuration</h1>
        <p className="text-sm text-slate-400">
          Configure financial market data providers, FinBERT model parameters, and database connections.
        </p>
      </div>

      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Server className="w-4 h-4 text-emerald-400" />
          System Diagnostics
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-slate-400 block font-sans">API Environment</span>
            <span className="text-slate-100 font-bold">{health?.environment || 'development'}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-slate-400 block font-sans">Database Driver</span>
            <span className="text-slate-100 font-bold">{health?.database.database_type || 'Async Engine'}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-slate-400 block font-sans">Redis Caching</span>
            <span className="text-slate-100 font-bold">{health?.redis.status || 'Active'}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-slate-400 block font-sans">Sentiment NLP Model</span>
            <span className="text-slate-100 font-bold">ProsusAI/finbert (HuggingFace)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
