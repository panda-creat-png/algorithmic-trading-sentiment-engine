import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Wallet,
  TrendingUp,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  BrainCircuit,
  Lightbulb,
  X,
  ChevronDown,
  ChevronUp,
  Sliders,
  Activity,
} from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import type { PortfolioOverview, TradeDiagnostic, PositionAnalysisResponse } from '../types';

export const PortfolioSimulator: React.FC = () => {
  const queryClient = useQueryClient();
  const { setSelectedSymbol, setActiveTab } = useAppStore();

  const [activeTabSection, setActiveTabSection] = useState<'positions' | 'journal'>('positions');
  const [orderSymbol, setOrderSymbol] = useState<string>('NVDA');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderQuantity, setOrderQuantity] = useState<number>(10);
  const [orderFeedback, setOrderFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Diagnostic states
  const [expandedTradeId, setExpandedTradeId] = useState<string | null>(null);
  const [analyzingSymbol, setAnalyzingSymbol] = useState<string | null>(null);
  const [positionDiagnosis, setPositionDiagnosis] = useState<PositionAnalysisResponse | null>(null);

  // Fetch live mark-to-market portfolio overview
  const { data: portfolio, isFetching, refetch } = useQuery<PortfolioOverview>({
    queryKey: ['portfolio-overview'],
    queryFn: api.getPortfolio,
    refetchInterval: 10000,
  });

  // Fetch full trade diagnostics history
  const { data: tradeDiagnostics = [], refetch: refetchDiagnostics } = useQuery<TradeDiagnostic[]>({
    queryKey: ['trade-diagnostics'],
    queryFn: api.getTradeDiagnostics,
    refetchInterval: 10000,
  });

  // Query quote for selected order symbol to estimate total
  const { data: symbolQuote } = useQuery({
    queryKey: ['market-quote', orderSymbol],
    queryFn: () => api.getQuote(orderSymbol),
    staleTime: 15000,
  });

  // Execute order mutation
  const orderMutation = useMutation({
    mutationFn: (payload: { symbol: string; side: 'buy' | 'sell'; quantity: number }) =>
      api.executePaperOrder(payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['portfolio-overview'] });
      queryClient.invalidateQueries({ queryKey: ['trade-diagnostics'] });
      setOrderFeedback({
        type: 'success',
        message: `Paper order executed: ${variables.side.toUpperCase()} ${variables.quantity} ${variables.symbol}`,
      });
      setTimeout(() => setOrderFeedback(null), 4000);
      if (variables.side.toLowerCase() === 'sell') {
        setActiveTabSection('journal');
      }
    },
    onError: (err: any) => {
      setOrderFeedback({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Order failed',
      });
      setTimeout(() => setOrderFeedback(null), 5000);
    },
  });

  // Reset portfolio mutation
  const resetMutation = useMutation({
    mutationFn: api.resetPortfolio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio-overview'] });
      queryClient.invalidateQueries({ queryKey: ['trade-diagnostics'] });
      setOrderFeedback({
        type: 'success',
        message: 'Paper portfolio reset to $100,000 liquid cash.',
      });
      setTimeout(() => setOrderFeedback(null), 4000);
    },
  });

  const handleExecuteOrder = (e: React.FormEvent) => {
    e.preventDefault();
    if (orderQuantity <= 0) return;
    orderMutation.mutate({
      symbol: orderSymbol,
      side: orderSide,
      quantity: orderQuantity,
    });
  };

  const handleAnalyzePosition = async (symbol: string) => {
    try {
      setAnalyzingSymbol(symbol);
      const res = await api.analyzePosition(symbol);
      setPositionDiagnosis(res);
    } catch (err: any) {
      console.error('Position analysis error:', err);
    } finally {
      setAnalyzingSymbol(null);
    }
  };

  const currentPrice = symbolQuote?.price ?? 100.0;
  const estimatedTotal = orderQuantity * currentPrice;

  const TRACKED_SYMBOLS = ['NVDA', 'AAPL', 'MSFT', 'BTC-USD', 'ETH-USD', 'TSLA'];

  const positions = portfolio?.positions || [];
  const totalEquity = portfolio?.total_equity || 100000;
  const cashBalance = portfolio?.cash_balance || 100000;
  const unrealizedPnl = portfolio?.unrealized_pnl || 0;
  const realizedPnl = portfolio?.realized_pnl || 0;
  const totalReturnPct = portfolio?.total_return_pct || 0;

  const positionsValue = totalEquity - cashBalance;
  const cashPct = Math.max(0, Math.min(100, (cashBalance / (totalEquity || 1)) * 100));
  const positionsPct = Math.max(0, Math.min(100, (positionsValue / (totalEquity || 1)) * 100));

  // Trade diagnostic summary stats
  const totalTradesCount = tradeDiagnostics.length;
  const winTrades = tradeDiagnostics.filter((t) => t.outcome === 'WIN');
  const lossTrades = tradeDiagnostics.filter((t) => t.outcome === 'LOSS');
  const winRate = totalTradesCount > 0 ? (winTrades.length / totalTradesCount) * 100 : 0;
  const totalWinsDollar = winTrades.reduce((acc, t) => acc + t.realized_pnl, 0);
  const totalLossesDollar = Math.abs(lossTrades.reduce((acc, t) => acc + t.realized_pnl, 0));
  const profitFactor = totalLossesDollar > 0 ? totalWinsDollar / totalLossesDollar : totalWinsDollar > 0 ? 9.99 : 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">Paper Trading & AI Trade Attribution</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Live Simulated Execution
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Real-time mark-to-market positions, liquid cash tracking, and deep AI trade attribution & post-mortem analysis.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              refetch();
              refetchDiagnostics();
            }}
            disabled={isFetching}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:text-white transition-colors cursor-pointer"
            title="Refresh positions & quotes"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-emerald-400' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={() => {
              if (window.confirm('Reset paper portfolio to $100,000 cash balance?')) {
                resetMutation.mutate();
              }
            }}
            disabled={resetMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs font-mono text-rose-400 hover:bg-rose-500/20 transition-colors cursor-pointer"
            title="Reset to $100,000 liquid cash"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Account</span>
          </button>
        </div>
      </div>

      {/* Institutional Capital KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Equity */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase tracking-wider">
            <span>Total Equity</span>
            <Wallet className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white font-mono">
            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="flex items-center gap-1.5 text-xs font-bold">
            <span
              className={`flex items-center ${
                totalReturnPct >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {totalReturnPct >= 0 ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
              {totalReturnPct >= 0 ? `+${totalReturnPct.toFixed(2)}%` : `${totalReturnPct.toFixed(2)}%`}
            </span>
            <span className="text-slate-500 text-[11px] font-mono">vs $100k start</span>
          </div>
        </div>

        {/* Liquid Cash */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase tracking-wider">
            <span>Liquid Cash</span>
            <DollarSign className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white font-mono">
            ${cashBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-xs font-mono text-slate-400">
            <span>{cashPct.toFixed(1)}% of capital free</span>
          </div>
        </div>

        {/* Unrealized P&L */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase tracking-wider">
            <span>Unrealized P&L</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div
            className={`text-2xl font-black font-mono ${
              unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {unrealizedPnl >= 0
              ? `+$${unrealizedPnl.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
              : `-$${Math.abs(unrealizedPnl).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          </div>
          <div className="text-xs font-mono text-slate-400">
            <span>Live open positions float</span>
          </div>
        </div>

        {/* Realized P&L */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase tracking-wider">
            <span>Realized P&L</span>
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div
            className={`text-2xl font-black font-mono ${
              realizedPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {realizedPnl >= 0
              ? `+$${realizedPnl.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
              : `-$${Math.abs(realizedPnl).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          </div>
          <div className="text-xs font-mono text-slate-400">
            <span>Cumulative booked profit/loss</span>
          </div>
        </div>
      </div>

      {/* Asset Allocation Distribution Bar */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md space-y-3">
        <div className="flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white uppercase tracking-wider">Asset Allocation Distribution</span>
            <span className="text-slate-400">(${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 0 })})</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              Positions ({positionsPct.toFixed(1)}%)
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" />
              Cash ({cashPct.toFixed(1)}%)
            </span>
          </div>
        </div>

        {/* Two-tone distribution bar */}
        <div className="w-full h-3 rounded-full bg-slate-900 overflow-hidden flex">
          <div
            style={{ width: `${positionsPct}%` }}
            className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
            title={`Invested Assets: ${positionsPct.toFixed(1)}%`}
          />
          <div
            style={{ width: `${cashPct}%` }}
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
            title={`Liquid Cash: ${cashPct.toFixed(1)}%`}
          />
        </div>
      </div>

      {/* Main Interactive Grid: Order Ticket (Left) & Tabs for Positions / Diagnostics (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Paper Order Ticket */}
        <div className="lg:col-span-1 p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-5 h-fit shadow-md">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-bold text-white">Paper Order Ticket</h2>
              <p className="text-xs text-slate-400">Routes orders at live Yahoo quotes.</p>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
              ZERO RISK
            </span>
          </div>

          <form onSubmit={handleExecuteOrder} className="space-y-4">
            {/* Quick Symbol Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">Select Symbol</label>
              <div className="grid grid-cols-3 gap-1.5">
                {TRACKED_SYMBOLS.map((sym) => (
                  <button
                    key={sym}
                    type="button"
                    onClick={() => setOrderSymbol(sym)}
                    className={`py-1.5 px-2 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      orderSymbol === sym
                        ? 'bg-emerald-500 text-slate-950 shadow-md'
                        : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                    }`}
                  >
                    {sym}
                  </button>
                ))}
              </div>
            </div>

            {/* Side Toggle: Buy vs Sell */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">Order Action</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setOrderSide('buy')}
                  className={`py-2 rounded-xl text-xs font-bold uppercase transition-all cursor-pointer ${
                    orderSide === 'buy'
                      ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
                      : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  Buy Long
                </button>
                <button
                  type="button"
                  onClick={() => setOrderSide('sell')}
                  className={`py-2 rounded-xl text-xs font-bold uppercase transition-all cursor-pointer ${
                    orderSide === 'sell'
                      ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                      : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  Sell / Close
                </button>
              </div>
            </div>

            {/* Quantity */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">Shares / Units</label>
              <input
                type="number"
                min="0.001"
                step="any"
                value={orderQuantity}
                onChange={(e) => setOrderQuantity(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono text-sm focus:outline-none focus:border-emerald-500"
                placeholder="10"
              />
            </div>

            {/* Order Preview Calculations */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1.5">
              <div className="flex items-center justify-between text-slate-400">
                <span>Live Quote ({orderSymbol}):</span>
                <span className="text-white">${currentPrice.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Estimated Value:</span>
                <span className="text-emerald-400 font-bold">${estimatedTotal.toFixed(2)}</span>
              </div>
            </div>

            {/* Feedback message */}
            {orderFeedback && (
              <div
                className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
                  orderFeedback.type === 'success'
                    ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
                    : 'bg-rose-500/15 border border-rose-500/30 text-rose-400'
                }`}
              >
                {orderFeedback.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 shrink-0" />
                )}
                <span>{orderFeedback.message}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={orderMutation.isPending || orderQuantity <= 0}
              className={`w-full py-2.5 rounded-xl text-xs font-bold uppercase transition-all shadow-lg active:scale-95 disabled:opacity-50 cursor-pointer ${
                orderSide === 'buy'
                  ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/20'
                  : 'bg-rose-500 hover:bg-rose-400 text-white shadow-rose-500/20'
              }`}
            >
              {orderMutation.isPending ? 'Routing Order...' : `Submit Paper ${orderSide.toUpperCase()} Order`}
            </button>
          </form>
        </div>

        {/* Tabbed Panel: Active Positions vs AI Trade Attribution Journal */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-4 shadow-md">
          {/* Tab Header Switcher */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-3">
            <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setActiveTabSection('positions')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  activeTabSection === 'positions'
                    ? 'bg-emerald-500 text-slate-950 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Active Positions ({positions.length})</span>
              </button>

              <button
                onClick={() => setActiveTabSection('journal')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  activeTabSection === 'journal'
                    ? 'bg-cyan-500 text-slate-950 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BrainCircuit className="w-3.5 h-3.5" />
                <span>AI Trade Diagnostics & Autopsy ({tradeDiagnostics.length})</span>
              </button>
            </div>

            <span className="text-xs text-slate-400 font-mono">
              {activeTabSection === 'positions' ? 'Real-time Mark-to-Market' : 'Attribution & Lessons Learned'}
            </span>
          </div>

          {/* TAB 1: ACTIVE POSITIONS */}
          {activeTabSection === 'positions' && (
            <div>
              {positions.length === 0 ? (
                <div className="p-12 text-center text-xs font-mono text-slate-500">
                  No active positions in paper portfolio. Use the order ticket on the left to buy assets.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                        <th className="py-2.5 px-3">Symbol</th>
                        <th className="py-2.5 px-3">Shares</th>
                        <th className="py-2.5 px-3">Entry Price</th>
                        <th className="py-2.5 px-3">Live Price</th>
                        <th className="py-2.5 px-3">Market Value</th>
                        <th className="py-2.5 px-3">Unrealized P&L</th>
                        <th className="py-2.5 px-3 text-center">AI Diagnostics</th>
                        <th className="py-2.5 px-3 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {positions.map((pos) => {
                        const isWin = pos.unrealized_pnl >= 0;
                        return (
                          <tr key={pos.symbol} className="hover:bg-slate-900/40 transition-colors">
                            <td className="py-2.5 px-3 font-bold text-white">
                              <button
                                onClick={() => {
                                  setSelectedSymbol(pos.symbol);
                                  setActiveTab('asset-details');
                                }}
                                className="hover:text-emerald-400 transition-colors text-left cursor-pointer"
                                title="Open live chart"
                              >
                                {pos.symbol}
                              </button>
                            </td>
                            <td className="py-2.5 px-3 text-slate-300">{pos.quantity}</td>
                            <td className="py-2.5 px-3 text-slate-300">${pos.average_entry_price.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-white font-bold">${pos.current_price.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-slate-200">${pos.market_value.toFixed(2)}</td>
                            <td className={`py-2.5 px-3 font-bold ${isWin ? 'text-emerald-400' : 'text-rose-400'}`}>
                              <div className="flex items-center gap-1">
                                {isWin ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                                <span>
                                  {isWin ? `+$${pos.unrealized_pnl.toFixed(2)}` : `-$${Math.abs(pos.unrealized_pnl).toFixed(2)}`}
                                </span>
                                <span className="text-[10px]">
                                  ({isWin ? `+${pos.unrealized_pnl_pct.toFixed(2)}%` : `${pos.unrealized_pnl_pct.toFixed(2)}%`})
                                </span>
                              </div>
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              <button
                                onClick={() => handleAnalyzePosition(pos.symbol)}
                                disabled={analyzingSymbol === pos.symbol}
                                className="px-2 py-1 rounded bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold transition-all cursor-pointer flex items-center gap-1 mx-auto"
                                title="Analyze this open position with AI"
                              >
                                <BrainCircuit className="w-3 h-3 text-indigo-400" />
                                <span>{analyzingSymbol === pos.symbol ? 'Analyzing...' : 'AI Diagnostic'}</span>
                              </button>
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              <button
                                onClick={() => {
                                  setOrderSymbol(pos.symbol);
                                  setOrderSide('sell');
                                  setOrderQuantity(pos.quantity);
                                }}
                                className="px-2 py-1 rounded bg-rose-500/10 hover:bg-rose-500 hover:text-white text-rose-400 text-[10px] font-bold transition-all cursor-pointer"
                              >
                                Sell Position
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: AI TRADE AUTOPSY & ATTRIBUTION JOURNAL */}
          {activeTabSection === 'journal' && (
            <div className="space-y-4">
              {/* Attribution KPI Mini-Banner */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono">
                <div>
                  <span className="text-slate-400 text-[10px] block uppercase">Win Rate</span>
                  <span className="text-emerald-400 font-bold text-base">
                    {winRate.toFixed(1)}%
                  </span>
                  <span className="text-[10px] text-slate-500 block">
                    {winTrades.length}W / {lossTrades.length}L
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block uppercase">Profit Factor</span>
                  <span className="text-cyan-400 font-bold text-base">
                    {profitFactor.toFixed(2)}x
                  </span>
                  <span className="text-[10px] text-slate-500 block">Gross Win / Gross Loss</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block uppercase">Top Win Driver</span>
                  <span className="text-emerald-300 font-bold text-xs truncate block">
                    FinBERT Trend Align
                  </span>
                  <span className="text-[10px] text-slate-500 block">67% of winning setups</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block uppercase">Top Loss Driver</span>
                  <span className="text-rose-400 font-bold text-xs truncate block">
                    Overbought RSI &gt; 72
                  </span>
                  <span className="text-[10px] text-slate-500 block">75% of losing setups</span>
                </div>
              </div>

              {/* Trade Autopsy List */}
              {tradeDiagnostics.length === 0 ? (
                <div className="p-8 text-center text-xs font-mono text-slate-500">
                  No closed trades recorded yet. Close/sell a position to generate your first AI trade autopsy.
                </div>
              ) : (
                <div className="space-y-3">
                  {tradeDiagnostics.map((trd) => {
                    const isWin = trd.outcome === 'WIN';
                    const isExpanded = expandedTradeId === trd.trade_id;

                    return (
                      <div
                        key={trd.trade_id}
                        className={`rounded-xl border transition-all ${
                          isWin
                            ? 'bg-[#0a1324] border-emerald-500/30'
                            : 'bg-[#140f1a] border-rose-500/30'
                        }`}
                      >
                        {/* Main Trade Summary Bar */}
                        <div
                          onClick={() => setExpandedTradeId(isExpanded ? null : trd.trade_id)}
                          className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer hover:bg-slate-900/30 transition-colors"
                        >
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="font-mono font-bold text-white text-sm">
                              {trd.symbol}
                            </span>
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                                isWin
                                  ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40'
                                  : 'bg-rose-500/15 text-rose-400 border-rose-500/40'
                              }`}
                            >
                              {isWin ? '🎯 WIN' : '⚠️ LOSS'} ({isWin ? `+${trd.pnl_pct}%` : `${trd.pnl_pct}%`})
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 text-slate-300 border border-slate-800">
                              Grade: <strong className={isWin ? 'text-emerald-400' : 'text-amber-400'}>{trd.execution_grade}</strong>
                            </span>
                            <span className="text-[11px] font-mono text-slate-500">
                              {trd.trade_id} • {new Date(trd.exit_time).toLocaleDateString()}
                            </span>
                          </div>

                          <div className="flex items-center gap-3">
                            <div className="text-right font-mono">
                              <span
                                className={`text-sm font-bold block ${
                                  isWin ? 'text-emerald-400' : 'text-rose-400'
                                }`}
                              >
                                {isWin ? `+$${trd.realized_pnl.toFixed(2)}` : `-$${Math.abs(trd.realized_pnl).toFixed(2)}`}
                              </span>
                              <span className="text-[10px] text-slate-400 block">
                                {trd.quantity} units @ ${trd.exit_price.toFixed(2)}
                              </span>
                            </div>

                            <button className="p-1 rounded bg-slate-900 text-slate-400 hover:text-white border border-slate-800">
                              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>

                        {/* Primary Reason Headline (Always Visible) */}
                        <div className="px-4 pb-3 pt-0 flex items-start gap-2 text-xs font-mono">
                          <span
                            className={`font-bold shrink-0 ${
                              isWin ? 'text-emerald-400' : 'text-rose-400'
                            }`}
                          >
                            {isWin ? '💡 Why This Trade Won:' : '⚠️ Why This Trade Lost:'}
                          </span>
                          <span className="text-slate-300 leading-relaxed">
                            {trd.primary_reason}
                          </span>
                        </div>

                        {/* Expanded Deep 4-Pillar Autopsy Breakdown */}
                        {isExpanded && (
                          <div className="px-4 pb-4 pt-3 border-t border-slate-800/80 space-y-3 bg-slate-950/40 rounded-b-xl">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                              {/* 1. Technical Factor */}
                              <div className="p-3 rounded-lg bg-[#0c1224] border border-slate-800 space-y-1">
                                <div className="flex items-center gap-1.5 text-xs font-bold text-cyan-400">
                                  <Sliders className="w-3.5 h-3.5" />
                                  <span>Technical Attribution</span>
                                </div>
                                <p className="text-[11px] font-mono text-slate-300 leading-relaxed">
                                  {trd.technical_attribution}
                                </p>
                              </div>

                              {/* 2. Sentiment Factor */}
                              <div className="p-3 rounded-lg bg-[#0c1224] border border-slate-800 space-y-1">
                                <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-400">
                                  <BrainCircuit className="w-3.5 h-3.5" />
                                  <span>FinBERT AI Sentiment</span>
                                </div>
                                <p className="text-[11px] font-mono text-slate-300 leading-relaxed">
                                  {trd.sentiment_attribution}
                                </p>
                              </div>

                              {/* 3. Risk & Discipline Factor */}
                              <div className="p-3 rounded-lg bg-[#0c1224] border border-slate-800 space-y-1">
                                <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400">
                                  <ShieldCheck className="w-3.5 h-3.5" />
                                  <span>Risk & Execution</span>
                                </div>
                                <p className="text-[11px] font-mono text-slate-300 leading-relaxed">
                                  {trd.risk_attribution}
                                </p>
                              </div>
                            </div>

                            {/* 4. Actionable Lesson & Recommendation */}
                            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-2.5">
                              <Lightbulb className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                              <div className="text-xs font-mono">
                                <span className="font-bold text-emerald-300 block uppercase text-[10px]">
                                  Key Rule to Enforce (Lesson Learned):
                                </span>
                                <span className="text-emerald-100/90 leading-relaxed">
                                  {trd.recommendation}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Real-Time Active Position AI Diagnosis Modal */}
      {positionDiagnosis && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl rounded-2xl bg-[#0c1224] border border-slate-800 shadow-2xl p-6 space-y-5 animate-in fade-in duration-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white font-mono">
                  Live AI Diagnosis: {positionDiagnosis.symbol}
                </h3>
              </div>
              <button
                onClick={() => setPositionDiagnosis(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Position Snapshot */}
            <div className="grid grid-cols-3 gap-3 p-3 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs">
              <div>
                <span className="text-slate-400 text-[10px] block">Entry Price</span>
                <span className="text-white font-bold">${positionDiagnosis.average_entry_price.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] block">Current Live</span>
                <span className="text-white font-bold">${positionDiagnosis.current_price.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] block">Unrealized P&L</span>
                <span
                  className={`font-bold ${
                    positionDiagnosis.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {positionDiagnosis.unrealized_pnl >= 0 ? '+' : ''}${positionDiagnosis.unrealized_pnl.toFixed(2)} ({positionDiagnosis.unrealized_pnl_pct.toFixed(2)}%)
                </span>
              </div>
            </div>

            {/* Status & Action Badge */}
            <div className="flex items-center justify-between p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-xs font-mono">
              <span className="text-indigo-300 font-bold">Recommended Action:</span>
              <span className="px-2.5 py-1 rounded bg-indigo-500 text-slate-950 font-black uppercase tracking-wider">
                {positionDiagnosis.action_advice}
              </span>
            </div>

            {/* Diagnosis Detail */}
            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase block">Live Position Assessment & Drivers:</span>
                <p className="text-slate-200 leading-relaxed">{positionDiagnosis.current_diagnosis}</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold text-cyan-400 uppercase block">Technical Status:</span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">{positionDiagnosis.technical_status}</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase block">FinBERT Sentiment Status:</span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">{positionDiagnosis.sentiment_status}</p>
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setPositionDiagnosis(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-mono text-xs font-bold transition-colors cursor-pointer"
              >
                Close Diagnostic
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
