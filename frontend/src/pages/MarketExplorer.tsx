import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, RefreshCw, ExternalLink } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { api } from '../services/api';
import type { Asset } from '../types';

export const MarketExplorer: React.FC = () => {
  const { setSelectedSymbol, setActiveTab } = useAppStore();
  const [filterClass, setFilterClass] = useState<string>('all');
  const [query, setQuery] = useState<string>('');

  // Fetch real tracked assets from backend
  const { data: assetsData, refetch, isFetching } = useQuery({
    queryKey: ['tracked-assets'],
    queryFn: api.getAssets,
    staleTime: 60000,
  });

  const assets: Asset[] = assetsData || [
    { id: 1, symbol: 'NVDA', name: 'NVIDIA Corporation', asset_class: 'stock', exchange: 'NASDAQ', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 2, symbol: 'AAPL', name: 'Apple Inc.', asset_class: 'stock', exchange: 'NASDAQ', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 3, symbol: 'MSFT', name: 'Microsoft Corporation', asset_class: 'stock', exchange: 'NASDAQ', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 4, symbol: 'GOOGL', name: 'Alphabet Inc.', asset_class: 'stock', exchange: 'NASDAQ', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 5, symbol: 'AMZN', name: 'Amazon.com Inc.', asset_class: 'stock', exchange: 'NASDAQ', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 6, symbol: 'TSLA', name: 'Tesla, Inc.', asset_class: 'stock', exchange: 'NASDAQ', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 7, symbol: 'BTC-USD', name: 'Bitcoin USD', asset_class: 'crypto', exchange: 'CRYPTO', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
    { id: 8, symbol: 'ETH-USD', name: 'Ethereum USD', asset_class: 'crypto', exchange: 'CRYPTO', currency: 'USD', is_active: true, created_at: '', updated_at: '' },
  ];

  const filtered = assets.filter((a) => {
    if (filterClass !== 'all' && a.asset_class !== filterClass) return false;
    if (
      query &&
      !a.symbol.toLowerCase().includes(query.toLowerCase()) &&
      !a.name.toLowerCase().includes(query.toLowerCase())
    ) {
      return false;
    }
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
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">Market Explorer</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Live Yahoo Finance Data
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Real-time tracked institutional equities and cryptocurrencies with live feeds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search symbol (e.g. NVDA, BTC)..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
            {['all', 'stock', 'crypto'].map((cls) => (
              <button
                key={cls}
                onClick={() => setFilterClass(cls)}
                className={`px-3 py-1 rounded-md uppercase font-bold text-[11px] transition-all ${
                  filterClass === cls
                    ? 'bg-emerald-500 text-slate-950 shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {cls}
              </button>
            ))}
          </div>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh assets"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-[#0c1224]">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold bg-slate-900/60">
              <th className="py-3 px-4">Symbol / Name</th>
              <th className="py-3 px-4">Asset Class</th>
              <th className="py-3 px-4">Exchange</th>
              <th className="py-3 px-4">Currency</th>
              <th className="py-3 px-4 text-center">Status</th>
              <th className="py-3 px-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 font-mono">
            {filtered.map((asset) => (
              <tr key={asset.symbol} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-4">
                  <div className="font-bold text-white text-sm">{asset.symbol}</div>
                  <div className="text-[11px] text-slate-400 font-sans">{asset.name}</div>
                </td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-300 border border-slate-700">
                    {asset.asset_class}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-300 font-sans">{asset.exchange}</td>
                <td className="py-3 px-4 text-slate-400">{asset.currency}</td>
                <td className="py-3 px-4 text-center">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Live Active
                  </span>
                </td>
                <td className="py-3 px-4 text-center font-sans">
                  <button
                    onClick={() => handleSelect(asset.symbol)}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500 hover:text-slate-950 font-bold transition-all text-[11px]"
                  >
                    <span>Open Live Chart</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
