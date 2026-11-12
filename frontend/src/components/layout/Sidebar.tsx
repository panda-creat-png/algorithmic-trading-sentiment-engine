import React from 'react';
import {
  LayoutDashboard,
  Globe,
  TrendingUp,
  Newspaper,
  BrainCircuit,
  Sliders,
  PlaySquare,
  Briefcase,
  BarChart3,
  Settings,
  ChevronLeft,
  Activity,
  ShieldCheck,
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import type { NavTab } from '../../types';

interface NavItem {
  id: NavTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'market-explorer', label: 'Market Explorer', icon: Globe },
  { id: 'asset-details', label: 'Asset Details', icon: TrendingUp },
  { id: 'news-sentiment', label: 'News & Sentiment', icon: Newspaper },
  { id: 'ai-insights', label: 'AI Insights', icon: BrainCircuit, badge: 'FinBERT' },
  { id: 'strategy-builder', label: 'Strategy Builder', icon: Sliders },
  { id: 'backtesting', label: 'Backtesting', icon: PlaySquare },
  { id: 'portfolio-simulator', label: 'Portfolio Simulator', icon: Briefcase },
  { id: 'performance-analytics', label: 'Performance Analytics', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <aside
      className={`relative flex flex-col h-screen border-r border-slate-800 bg-[#0a0f1d] transition-all duration-300 z-30 select-none ${
        sidebarCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div
        className={`flex items-center h-16 border-b border-slate-800/80 transition-all ${
          sidebarCollapsed ? 'justify-center px-2' : 'justify-between px-4'
        }`}
      >
        {sidebarCollapsed ? (
          /* When collapsed: show ONLY the centered full logo, NO arrow! */
          <button
            onClick={toggleSidebar}
            className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-700 shadow-lg shadow-emerald-500/20 text-white font-bold shrink-0 hover:scale-105 active:scale-95 transition-all cursor-pointer focus:outline-none"
            title="Expand sidebar"
          >
            <Activity className="w-5 h-5 text-emerald-100" />
          </button>
        ) : (
          /* When expanded: show logo + brand title on left, collapse button on right */
          <>
            <div
              onClick={() => setActiveTab('overview')}
              className="flex items-center gap-3 overflow-hidden cursor-pointer group"
              title="QuantMind AI"
            >
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-700 shadow-lg shadow-emerald-500/20 text-white font-bold shrink-0 group-hover:scale-105 transition-transform">
                <Activity className="w-5 h-5 text-emerald-100" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-extrabold tracking-tight text-white text-base leading-tight">
                  Quant<span className="text-emerald-400">Mind</span> AI
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400">
                  Institutional Quant
                </span>
              </div>
            </div>

            <button
              onClick={toggleSidebar}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors cursor-pointer"
              title="Collapse sidebar"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              } ${sidebarCollapsed ? 'justify-center px-2' : ''}`}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
              {!sidebarCollapsed && (
                <div className="flex items-center justify-between flex-1 truncate text-left">
                  <span className="truncate">{item.label}</span>
                  {item.badge && (
                    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Safety Notice & System Mode */}
      {!sidebarCollapsed ? (
        <div className="p-3 mx-3 mb-4 rounded-xl bg-slate-900/90 border border-slate-800 text-[11px] text-slate-400 space-y-1.5">
          <div className="flex items-center gap-1.5 font-semibold text-emerald-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>PAPER TRADING ONLY</span>
          </div>
          <p className="text-slate-500 leading-relaxed">
            Strict simulation environment. No real funds or execution orders.
          </p>
        </div>
      ) : (
        <div className="flex justify-center mb-4 text-emerald-400" title="Paper Trading Environment Active">
          <ShieldCheck className="w-5 h-5" />
        </div>
      )}
    </aside>
  );
};

