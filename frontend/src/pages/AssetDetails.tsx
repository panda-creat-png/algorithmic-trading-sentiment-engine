import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '../store/useAppStore';
import { api } from '../services/api';
import { LightweightCandleChart } from '../charts/LightweightCandleChart';
import {
  BarChart3,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Sliders,
  TrendingUp,
  Maximize2,
  Minimize2,
} from 'lucide-react';

export const AssetDetails: React.FC = () => {
  const { selectedSymbol } = useAppStore();
  const [timeframe, setTimeframe] = useState<string>('1d');
  const [candleLimit, setCandleLimit] = useState<number>(300);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1wk'];
  const DEPTHS = [100, 300, 500, 1000];

  // Fetch real OHLCV historical candles
  const {
    data: historyData,
    refetch: refetchHistory,
    isFetching: historyFetching,
  } = useQuery({
    queryKey: ['market-history', selectedSymbol, timeframe, candleLimit],
    queryFn: () => api.getMarketHistory(selectedSymbol, timeframe, candleLimit),
    staleTime: 30000,
  });

  // Fetch real-time live quote
  const { data: quoteData } = useQuery({
    queryKey: ['market-quote', selectedSymbol],
    queryFn: () => api.getQuote(selectedSymbol),
    refetchInterval: 10000,
  });

  // Fetch computed technical indicators & quantitative signals
  const { data: indicatorData, refetch: refetchIndicators } = useQuery({
    queryKey: ['technical-indicators', selectedSymbol, timeframe],
    queryFn: () => api.getTechnicalIndicators(selectedSymbol, timeframe, 60),
    staleTime: 30000,
  });

  const candles = historyData?.candles || [];
  const latestCandle = candles.length > 0 ? candles[candles.length - 1] : null;

  const isPositive = (quoteData?.change ?? 0) >= 0;

  const metrics = indicatorData?.latest_metrics || {};
  const signals = indicatorData?.signals || [];
  const bias = indicatorData?.bias || 'BULLISH';

  // Toggle fullscreen mode
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      setIsFullscreen(true);
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
      }
    } else {
      setIsFullscreen(false);
      if (document.fullscreenElement && document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
    }
  };

  // Keyboard and native fullscreen change listeners
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
        if (document.fullscreenElement && document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        }
      }
    };
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [isFullscreen]);

  // Lock body scroll when in fullscreen
  useEffect(() => {
    if (isFullscreen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isFullscreen]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Asset Header */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-700 flex items-center justify-center font-black text-xl text-white font-mono shadow-md">
            {selectedSymbol.slice(0, 2)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-white font-mono">{selectedSymbol}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-300 border border-slate-700">
                {selectedSymbol.includes('-USD') ? 'CRYPTO 24/7' : 'US EQUITY'}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                  bias === 'BULLISH'
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : bias === 'BEARISH'
                    ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                    : 'bg-slate-800 text-slate-300 border-slate-700'
                }`}
              >
                BIAS: {bias}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xl font-black text-white font-mono">
                ${(quoteData?.price ?? latestCandle?.close ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
              {quoteData && (
                <span className={`flex items-center text-xs font-bold ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {isPositive ? <ArrowUpRight className="w-4 h-4 mr-0.5" /> : <ArrowDownRight className="w-4 h-4 mr-0.5" />}
                  {isPositive ? `+${quoteData.change}` : quoteData.change} ({quoteData.change_percent}%)
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Timeframe & Depth Selector & Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Timeframes */}
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  timeframe === tf ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Candle History Depth */}
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <span className="text-[10px] font-mono text-slate-500 px-1 font-bold">DEPTH:</span>
            {DEPTHS.map((dep) => (
              <button
                key={dep}
                onClick={() => setCandleLimit(dep)}
                className={`px-2 py-0.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  candleLimit === dep ? 'bg-cyan-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
                title={`Load ${dep} historical candles`}
              >
                {dep}
              </button>
            ))}
          </div>

          <button
            onClick={() => {
              refetchHistory();
              refetchIndicators();
            }}
            disabled={historyFetching}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Refresh candles & indicators"
          >
            <RefreshCw className={`w-4 h-4 ${historyFetching ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* TradingView Lightweight Charts Viewport (Normal Card OR Fixed Fullscreen) */}
      <div
        className={
          isFullscreen
            ? 'fixed inset-0 z-50 bg-[#070c18] p-5 flex flex-col w-screen h-screen overflow-hidden'
            : 'p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md'
        }
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <BarChart3 className="w-5 h-5 text-emerald-400" />
            <span className="font-bold text-white text-sm font-mono">
              {selectedSymbol} • TradingView Chart
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-slate-900 text-emerald-400 border border-slate-800">
              {timeframe}
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-900 text-cyan-400 border border-slate-800 font-bold">
              {candles.length} candles
            </span>
            {candles.length > 0 && (
              <span className="text-xs text-slate-500 font-mono hidden md:inline">
                ({new Date(candles[0].timestamp).toLocaleDateString()} &rarr; {new Date(candles[candles.length - 1].timestamp).toLocaleDateString()})
              </span>
            )}
          </div>

          {/* If Fullscreen: Show Timeframe & Depth Pickers inside header */}
          {isFullscreen && (
            <div className="flex flex-wrap items-center gap-2">
              <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
                {TIMEFRAMES.map((tf) => (
                  <button
                    key={tf}
                    onClick={() => setTimeframe(tf)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      timeframe === tf ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {tf}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 px-1 font-bold">DEPTH:</span>
                {DEPTHS.map((dep) => (
                  <button
                    key={dep}
                    onClick={() => setCandleLimit(dep)}
                    className={`px-2 py-0.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      candleLimit === dep ? 'bg-cyan-500 text-slate-950 shadow' : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {dep}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* OHLCV metrics & Fullscreen Toggle Button */}
          <div className="flex items-center gap-3">
            {latestCandle && (
              <div className="hidden lg:flex items-center gap-3 text-xs font-mono text-slate-400">
                <span>O: <strong className="text-slate-200">{latestCandle.open.toFixed(2)}</strong></span>
                <span>H: <strong className="text-slate-200">{latestCandle.high.toFixed(2)}</strong></span>
                <span>L: <strong className="text-slate-200">{latestCandle.low.toFixed(2)}</strong></span>
                <span>C: <strong className="text-emerald-400">{latestCandle.close.toFixed(2)}</strong></span>
                <span>Vol: <strong className="text-slate-200">{latestCandle.volume.toLocaleString()}</strong></span>
                {latestCandle.vwap && (
                  <span>VWAP: <strong className="text-cyan-400">{latestCandle.vwap.toFixed(2)}</strong></span>
                )}
              </div>
            )}

            {/* Prominent Fullscreen Button */}
            <button
              onClick={toggleFullscreen}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer shadow-md ${
                isFullscreen
                  ? 'bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/40'
              }`}
              title={isFullscreen ? 'Exit Full Screen (ESC)' : 'Expand Chart to Full Screen'}
            >
              {isFullscreen ? (
                <>
                  <Minimize2 className="w-4 h-4" />
                  <span>Exit Fullscreen</span>
                  <span className="text-[10px] opacity-70 bg-rose-950 px-1 py-0.5 rounded ml-1 border border-rose-900">ESC</span>
                </>
              ) : (
                <>
                  <Maximize2 className="w-4 h-4" />
                  <span>Full Screen</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Real Candlestick Canvas */}
        <div className={`mt-4 ${isFullscreen ? 'flex-1 w-full h-full min-h-0' : ''}`}>
          <LightweightCandleChart
            candles={candles}
            symbol={selectedSymbol}
            timeframe={timeframe}
            isFullscreen={isFullscreen}
            onToggleFullscreen={toggleFullscreen}
          />
        </div>
      </div>

      {/* Real Computed Technical Indicators Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Box 1: Trend Indicators */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            <span>Trend & Moving Averages</span>
            <Sliders className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="mt-2 space-y-1.5 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">SMA 20:</span>
              <span className="text-slate-200 font-bold">${metrics.sma_20 ? metrics.sma_20.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">SMA 50:</span>
              <span className="text-slate-200 font-bold">${metrics.sma_50 ? metrics.sma_50.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">EMA 20:</span>
              <span className="text-slate-200 font-bold">${metrics.ema_20 ? metrics.ema_20.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between border-t border-slate-800/80 pt-1">
              <span className="text-slate-400">Trend State:</span>
              <span className="text-emerald-400 font-bold">
                {metrics.sma_20 && metrics.sma_50 && metrics.sma_20 > metrics.sma_50 ? 'BULLISH ALIGNMENT' : 'BEARISH ALIGNMENT'}
              </span>
            </div>
          </div>
        </div>

        {/* Box 2: Momentum & Volatility */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            <span>Momentum & Volatility</span>
            <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="mt-2 space-y-1.5 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">RSI (14):</span>
              <span
                className={`font-bold ${
                  (metrics.rsi_14 ?? 50) > 70
                    ? 'text-rose-400'
                    : (metrics.rsi_14 ?? 50) < 30
                    ? 'text-emerald-400'
                    : 'text-cyan-400'
                }`}
              >
                {metrics.rsi_14 ? metrics.rsi_14.toFixed(1) : '--'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">MACD Histogram:</span>
              <span className={`font-bold ${(metrics.macd_hist ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {metrics.macd_hist ? metrics.macd_hist.toFixed(3) : '--'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">ATR (14):</span>
              <span className="text-slate-200 font-bold">${metrics.atr_14 ? metrics.atr_14.toFixed(2) : '--'}</span>
            </div>
            <div className="flex justify-between border-t border-slate-800/80 pt-1">
              <span className="text-slate-400">Bollinger Upper:</span>
              <span className="text-slate-300 font-bold">${metrics.bb_upper ? metrics.bb_upper.toFixed(2) : '--'}</span>
            </div>
          </div>
        </div>

        {/* Box 3: Quantitative Signals */}
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            <span>Quantitative Signals</span>
            <Zap className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="mt-2 space-y-2">
            {signals.length === 0 ? (
              <span className="text-xs text-slate-500 font-mono">No active breakout triggers on {timeframe}</span>
            ) : (
              signals.map((sig: string, i: number) => (
                <div
                  key={i}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] font-mono text-amber-300"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  {sig}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
