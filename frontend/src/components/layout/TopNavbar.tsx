import React, { useState, useEffect } from 'react';
import {
  Search,
  Bell,
  Sun,
  Moon,
  Database,
  Server,
  Zap,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { useHealth } from '../../hooks/useHealth';

export const TopNavbar: React.FC = () => {
  const {
    selectedSymbol,
    setSelectedSymbol,
    searchQuery,
    setSearchQuery,
    isDarkTheme,
    toggleTheme,
    health,
    currentUser,
    setActiveTab,
  } = useAppStore();

  useHealth(); // activate polling

  const [currentTimeUtc, setCurrentTimeUtc] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTimeUtc(now.toUTCString().slice(17, 25) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setSelectedSymbol(searchQuery.trim().toUpperCase());
      setSearchQuery('');
    }
  };

  const getStatusBadge = (status?: string) => {
    if (status === 'connected' || status === 'ok') {
      return (
        <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          ONLINE
        </span>
      );
    }
    if (status === 'fallback_active' || status === 'degraded') {
      return (
        <span className="flex items-center gap-1 text-[11px] font-medium text-amber-400">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          FALLBACK
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-[11px] font-medium text-rose-400">
        <XCircle className="w-3.5 h-3.5 text-rose-400" />
        OFFLINE
      </span>
    );
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0c1224] flex items-center justify-between px-6 z-20">
      {/* Search Bar */}
      <form onSubmit={handleSearchSubmit} className="relative w-80 max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={`Search ticker (e.g. ${selectedSymbol}, BTC-USD)...`}
          className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-slate-900 border border-slate-700/80 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
        />
      </form>

      {/* Market Status & Connection Badges */}
      <div className="flex items-center gap-5">
        {/* Market Status Pill */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-semibold text-slate-300">MARKET OPEN</span>
          <span className="text-slate-500 font-mono text-[11px]">{currentTimeUtc}</span>
        </div>

        {/* Real-time Connection Status Indicators */}
        <div className="hidden md:flex items-center gap-3 px-3 py-1 rounded-lg bg-slate-900/70 border border-slate-800/80">
          {/* Backend API */}
          <div className="flex items-center gap-1.5" title={`FastAPI Backend: ${health?.status || 'Connecting...'}`}>
            <Server className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">API:</span>
            {getStatusBadge(health?.status)}
          </div>

          <div className="w-[1px] h-3 bg-slate-800" />

          {/* Database */}
          <div
            className="flex items-center gap-1.5"
            title={`Database: ${health?.database.database_type || 'SQLAlchemy'} (${health?.database.latency_ms ?? '--'} ms)`}
          >
            <Database className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">DB:</span>
            {getStatusBadge(health?.database.status)}
          </div>

          <div className="w-[1px] h-3 bg-slate-800" />

          {/* Redis */}
          <div
            className="flex items-center gap-1.5"
            title={`Redis / Cache: ${health?.redis.backend || 'Redis'} (${health?.redis.latency_ms ?? '--'} ms)`}
          >
            <Zap className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">REDIS:</span>
            {getStatusBadge(health?.redis.status)}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors"
            title="Toggle color mode"
          >
            {isDarkTheme ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <button
            className="relative p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors"
            title="System notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500"></span>
          </button>

          {/* User Profile Avatar */}
          <button
            onClick={() => setActiveTab('settings')}
            className="flex items-center gap-2 pl-2 border-l border-slate-800 hover:opacity-85 transition-opacity text-left"
            title="View Account & Settings"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center text-xs font-bold text-white shadow-sm font-mono">
              {currentUser?.full_name ? currentUser.full_name.slice(0, 2).toUpperCase() : 'QM'}
            </div>
            <div className="hidden xl:flex flex-col text-left">
              <span className="text-xs font-semibold text-slate-200">
                {currentUser?.full_name || 'Institutional Quant'}
              </span>
              <span className="text-[10px] text-emerald-400 font-mono">
                {currentUser ? 'AUTHENTICATED' : 'GUEST / LOCAL'}
              </span>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
};

