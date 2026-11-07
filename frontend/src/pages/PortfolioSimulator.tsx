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
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import type { PortfolioOverview } from '../types';

export const PortfolioSimulator: React.FC = () => {
  const queryClient = useQueryClient();
  const { setSelectedSymbol, setActiveTab } = useAppStore();

  const [orderSymbol, setOrderSymbol] = useState<string>('NVDA');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderQuantity, setOrderQuantity] = useState<number>(10);
  const [orderFeedback, setOrderFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Fetch live mark-to-market portfolio overview
  const { data: portfolio, isFetching, refetch } = useQuery<PortfolioOverview>({
    queryKey: ['portfolio-overview'],
    queryFn: api.getPortfolio,
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio-overview'] });
      setOrderFeedback({
        type: 'success',
        message: `Paper order executed: ${orderSide.toUpperCase()} ${orderQuantity} ${orderSymbol}`,
      });
      setTimeout(() => setOrderFeedback(null), 4000);
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

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">Paper Trading & Portfolio Simulator</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Live Simulated Execution
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Real-time mark-to-market positions, liquid cash tracking, and zero-risk paper order routing.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-emerald-400' : ''}`} />
            <span>Mark to Market</span>
          </button>

          <button
            onClick={() => {
              if (window.confirm('Reset paper portfolio to initial $100,000 cash balance?')) {
                resetMutation.mutate();
              }
            }}
            disabled={resetMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Account</span>
          </button>
        </div>
      </div>

      {/* Safety / Paper Trading Banner */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <span className="font-bold text-emerald-400">Paper Trading Sandbox Guarantee</span>
          <p className="text-slate-400 leading-relaxed">
            All orders executed here are paper simulated using live market data feeds. No real capital is ever deployed and no real financial brokerage accounts are accessed.
          </p>
        </div>
      </div>

      {/* Key Portfolio Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400">
            <span>Total Portfolio Equity</span>
            <Wallet className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl lg:text-3xl font-black text-white font-mono mt-1">
            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className={`text-xs font-mono font-bold mt-1 block ${totalReturnPct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {totalReturnPct >= 0 ? `+${totalReturnPct.toFixed(2)}%` : `${totalReturnPct.toFixed(2)}%`} Total Return
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400">
            <span>Available Liquid Cash</span>
            <DollarSign className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl lg:text-3xl font-black text-white font-mono mt-1">
            ${cashBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-xs text-slate-400 font-mono mt-1 block">
            {cashPct.toFixed(1)}% of Portfolio
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400">
            <span>Unrealized Open P&L</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className={`text-2xl lg:text-3xl font-black font-mono mt-1 ${unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {unrealizedPnl >= 0 ? `+$${unrealizedPnl.toFixed(2)}` : `-$${Math.abs(unrealizedPnl).toFixed(2)}`}
          </div>
          <span className="text-xs text-slate-400 font-mono mt-1 block">
            Across {positions.length} active positions
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400">
            <span>Realized Closed P&L</span>
            <DollarSign className="w-4 h-4 text-purple-400" />
          </div>
          <div className={`text-2xl lg:text-3xl font-black font-mono mt-1 ${realizedPnl >= 0 ? 'text-purple-400' : 'text-rose-400'}`}>
            {realizedPnl >= 0 ? `+$${realizedPnl.toFixed(2)}` : `-$${Math.abs(realizedPnl).toFixed(2)}`}
          </div>
          <span className="text-xs text-slate-400 font-mono mt-1 block">
            Cumulative profits booked
          </span>
        </div>
      </div>

      {/* Asset Allocation Breakdown Bar */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span className="font-bold text-white uppercase tracking-wider">Asset Allocation Distribution</span>
          <div className="flex items-center gap-4 text-slate-400 font-mono">
            <span>Invested Positions: <strong className="text-emerald-400">{positionsPct.toFixed(1)}%</strong> (${positionsValue.toLocaleString(undefined, { maximumFractionDigits: 0 })})</span>
            <span>Liquid Cash: <strong className="text-cyan-400">{cashPct.toFixed(1)}%</strong> (${cashBalance.toLocaleString(undefined, { maximumFractionDigits: 0 })})</span>
          </div>
        </div>
        <div className="w-full h-3 rounded-full bg-slate-900 overflow-hidden flex">
          <div style={{ width: `${positionsPct}%` }} className="h-full bg-emerald-500 transition-all duration-500"></div>
          <div style={{ width: `${cashPct}%` }} className="h-full bg-cyan-500 transition-all duration-500"></div>
        </div>
      </div>

      {/* Order Ticket & Active Positions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Paper Order Ticket */}
        <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col justify-between">
          <form onSubmit={handleExecuteOrder} className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white">Paper Order Ticket</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">
                Market Order
              </span>
            </div>

            {/* Symbol quick buttons */}
            <div>
              <label className="text-xs text-slate-400 font-semibold mb-1 block">Target Symbol</label>
              <div className="grid grid-cols-3 gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
                {TRACKED_SYMBOLS.map((sym) => (
                  <button
                    key={sym}
                    type="button"
                    onClick={() => setOrderSymbol(sym)}
                    className={`py-1.5 text-xs font-mono font-bold rounded-lg transition-all ${
                      orderSymbol === sym
                        ? 'bg-emerald-500 text-slate-950 shadow'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {sym}
                  </button>
                ))}
              </div>
            </div>

            {/* Buy / Sell Side Selector */}
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setOrderSide('buy')}
                className={`py-2 rounded-xl text-xs font-bold uppercase transition-all ${
                  orderSide === 'buy'
                    ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
                    : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                BUY / LONG
              </button>
              <button
                type="button"
                onClick={() => setOrderSide('sell')}
                className={`py-2 rounded-xl text-xs font-bold uppercase transition-all ${
                  orderSide === 'sell'
                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                    : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                SELL / CLOSE
              </button>
            </div>

            {/* Shares Quantity */}
            <div>
              <label className="text-xs text-slate-400 font-semibold mb-1 block">Quantity / Shares</label>
              <input
                type="number"
                step="any"
                min="0.001"
                value={orderQuantity}
                onChange={(e) => setOrderQuantity(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white text-xs font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Estimated execution details */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1.5 font-mono">
              <div className="flex items-center justify-between text-slate-400">
                <span>Market Price:</span>
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
              className={`w-full py-2.5 rounded-xl text-xs font-bold uppercase transition-all shadow-lg active:scale-95 disabled:opacity-50 ${
                orderSide === 'buy'
                  ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/20'
                  : 'bg-rose-500 hover:bg-rose-400 text-white shadow-rose-500/20'
              }`}
            >
              {orderMutation.isPending ? 'Routing Order...' : `Submit Paper ${orderSide.toUpperCase()} Order`}
            </button>
          </form>
        </div>

        {/* Live Active Positions Table */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#0c1224] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white">Active Portfolio Positions</h2>
              <p className="text-xs text-slate-400">Marked to live market quotes in real time.</p>
            </div>
            <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
              {positions.length} Assets
            </span>
          </div>

          {positions.length === 0 ? (
            <div className="p-12 text-center text-xs font-mono text-slate-500">
              No active positions in paper portfolio. Use the order ticket to buy assets.
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
                            className="hover:text-emerald-400 transition-colors text-left"
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
                            <span className="text-[10px]">({isWin ? `+${pos.unrealized_pnl_pct.toFixed(2)}%` : `${pos.unrealized_pnl_pct.toFixed(2)}%`})</span>
                          </div>
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <button
                            onClick={() => {
                              setOrderSymbol(pos.symbol);
                              setOrderSide('sell');
                              setOrderQuantity(pos.quantity);
                            }}
                            className="px-2 py-1 rounded bg-rose-500/10 hover:bg-rose-500 hover:text-white text-rose-400 text-[10px] font-bold transition-all"
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
      </div>
    </div>
  );
};
