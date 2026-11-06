import React, { useState } from 'react';
import { Search, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export const MarketExplorer: React.FC = () => {
  const { setSelectedSymbol, setActiveTab } = useAppStore();
  const [filterClass, setFilterClass] = useState<string>('all');
  const [query, setQuery] = useState<string>('');

  const ASSETS = [
    { symbol: 'NVDA', name: 'NVIDIA Corporation', class: 'stock', exchange: 'NASDAQ', price: 138.25, change: 4.82, volume: '58.4M', cap: '$3.40T', rsi: 68.2 },
    { symbol: 'AAPL', name: 'Apple Inc.', class: 'stock', exchange: 'NASDAQ', price: 227.40, change: 1.15, volume: '44.1M', cap: '$3.48T', rsi: 54.1 },
    { symbol: 'MSFT', name: 'Microsoft Corporation', class: 'stock', exchange: 'NASDAQ', price: 422.80, change: -0.45, volume: '22.8M', cap: '$3.14T', rsi: 49.8 },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', class: 'stock', exchange: 'NASDAQ', price: 178.50, change: 0.85, volume: '19.4M', cap: '$2.21T', rsi: 57.3 },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', class: 'stock', exchange: 'NASDAQ', price: 186.20, change: -1.20, volume: '28.1M', cap: '$1.94T', rsi: 46.5 },
    { symbol: 'TSLA', name: 'Tesla Inc.', class: 'stock', exchange: 'NASDAQ', price: 254.30, change: -2.80, volume: '62.0M', cap: '$812B', rsi: 42.1 },
    { symbol: 'BTC-USD', name: 'Bitcoin USD', class: 'crypto', exchange: 'CRYPTO', price: 66420.00, change: 3.20, volume: '$32.1B', cap: '$1.31T', rsi: 64.9 },
    { symbol: 'ETH-USD', name: 'Ethereum USD', class: 'crypto', exchange: 'CRYPTO', price: 3480.00, change: 2.15, volume: '$18.4B', cap: '$418B', rsi: 61.3 },
  ];

  const filtered = ASSETS.filter((a) => {
    if (filterClass !== 'all' && a.class !== filterClass) return false;
    if (query && !a.symbol.toLowerCase().includes(query.toLowerCase()) && !a.name.toLowerCase().includes(query.toLowerCase())) return false;
    return true;
  });

  const handleSelect = (sym: string) => {
    setSelectedSymbol(sym);
    setActiveTab('asset-details');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">Market Explorer</h1>
          <p className="text-sm text-slate-400">Real-time tracked institutional multi-asset universe.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter by ticker or name..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
            {['all', 'stock', 'crypto'].map((cls) => (
              <button
                key={cls}
                onClick={() => setFilterClass(cls)}
                className={`px-3 py-1 rounded-md uppercase font-bold text-[11px] transition-all ${
                  filterClass === cls ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {cls}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-[#0c1224]">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold bg-slate-900/60">
              <th className="py-3 px-4">Symbol / Name</th>
              <th className="py-3 px-4">Class</th>
              <th className="py-3 px-4 text-right">Price</th>
              <th className="py-3 px-4 text-right">24h Change</th>
              <th className="py-3 px-4 text-right">Volume</th>
              <th className="py-3 px-4 text-right">Market Cap</th>
              <th className="py-3 px-4 text-right">RSI (14)</th>
              <th className="py-3 px-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 font-mono">
            {filtered.map((asset) => {
              const isPos = asset.change >= 0;
              return (
                <tr key={asset.symbol} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-bold text-white text-sm">{asset.symbol}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{asset.name}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {asset.class}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-slate-100">
                    ${asset.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className={`inline-flex items-center font-bold ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isPos ? <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> : <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
                      {isPos ? `+${asset.change}%` : `${asset.change}%`}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300">{asset.volume}</td>
                  <td className="py-3 px-4 text-right text-slate-400">{asset.cap}</td>
                  <td className="py-3 px-4 text-right font-semibold">
                    <span className={asset.rsi > 70 ? 'text-rose-400' : asset.rsi < 30 ? 'text-emerald-400' : 'text-slate-300'}>
                      {asset.rsi}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center font-sans">
                    <button
                      onClick={() => handleSelect(asset.symbol)}
                      className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500 hover:text-slate-950 font-bold transition-all text-[11px]"
                    >
                      Analyze
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
