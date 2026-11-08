import React, { useEffect, useRef } from 'react';
import {
  createChart,
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from 'lightweight-charts';
import type { Candle } from '../types';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Compass } from 'lucide-react';

interface LightweightCandleChartProps {
  candles: Candle[];
  symbol: string;
  timeframe: string;
}

export const LightweightCandleChart: React.FC<LightweightCandleChartProps> = ({
  candles,
  symbol,
  timeframe,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create TradingView Chart instance with deep navy institutional styling
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#090e1c' },
        textColor: '#94a3b8',
        fontSize: 12,
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      },
      grid: {
        vertLines: { color: 'rgba(30, 41, 59, 0.4)' },
        horzLines: { color: 'rgba(30, 41, 59, 0.4)' },
      },
      crosshair: {
        vertLine: {
          color: '#38bdf8',
          width: 1,
          style: 1,
          labelBackgroundColor: '#0f172a',
        },
        horzLine: {
          color: '#38bdf8',
          width: 1,
          style: 1,
          labelBackgroundColor: '#0f172a',
        },
      },
      timeScale: {
        borderColor: '#1e293b',
        timeVisible: timeframe !== '1d' && timeframe !== '1wk',
        secondsVisible: false,
        rightOffset: 6,
        barSpacing: 9,
        minBarSpacing: 0.5,
        fixLeftEdge: true, // Prevents scrolling past the oldest candle into an empty void!
        fixRightEdge: false,
      },
      rightPriceScale: {
        borderColor: '#1e293b',
        autoScale: true,
      },
      handleScale: {
        mouseWheel: true,
        pinch: true,
        axisPressedMouseMove: { time: true, price: true },
      },
      handleScroll: {
        mouseWheel: false,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
    });

    chartRef.current = chart;

    // 1. Candlestick Series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });
    candleSeriesRef.current = candleSeries;

    // 2. Volume Histogram Series (scaled down at bottom)
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#0ea5e9',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
    });

    chart.priceScale('volume').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });
    volumeSeriesRef.current = volumeSeries;

    // Resize observer for responsive layout
    const resizeObserver = new ResizeObserver((entries) => {
      if (entries.length === 0 || !entries[0].contentRect) return;
      const { width, height } = entries[0].contentRect;
      chart.applyOptions({ width, height });
    });

    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [timeframe]);

  // Update chart data whenever candles change
  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || candles.length === 0) return;

    // Format candles for TradingView (time in seconds or YYYY-MM-DD)
    const formattedCandles = candles.map((c) => {
      const timeInSec = Math.floor(new Date(c.timestamp).getTime() / 1000) as UTCTimestamp;
      return {
        time: timeInSec,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      };
    });

    // Format volume histogram
    const formattedVolumes = candles.map((c) => {
      const timeInSec = Math.floor(new Date(c.timestamp).getTime() / 1000) as UTCTimestamp;
      return {
        time: timeInSec,
        value: c.volume,
        color: c.close >= c.open ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)',
      };
    });

    try {
      candleSeriesRef.current.setData(formattedCandles);
      volumeSeriesRef.current.setData(formattedVolumes);

      const totalBars = formattedCandles.length;
      if (totalBars > 0 && chartRef.current) {
        // Show the latest 75 candles comfortably zoomed in with breathing room on the right
        const visibleBars = Math.min(totalBars, 75);
        chartRef.current.timeScale().setVisibleLogicalRange({
          from: Math.max(0, totalBars - visibleBars),
          to: totalBars + 5,
        });
      }
    } catch (err) {
      console.warn('Error rendering candles in chart:', err);
    }
  }, [candles]);

  const handleResetToLatest = () => {
    if (!chartRef.current || candles.length === 0) return;
    const totalBars = candles.length;
    const visibleBars = Math.min(totalBars, 75);
    chartRef.current.timeScale().setVisibleLogicalRange({
      from: Math.max(0, totalBars - visibleBars),
      to: totalBars + 5,
    });
  };

  const handleFitAll = () => {
    if (!chartRef.current) return;
    chartRef.current.timeScale().fitContent();
  };

  const handleZoomIn = () => {
    if (!chartRef.current) return;
    const range = chartRef.current.timeScale().getVisibleLogicalRange();
    if (!range) return;
    const barsCount = range.to - range.from;
    const delta = Math.max(2, Math.floor(barsCount * 0.2));
    chartRef.current.timeScale().setVisibleLogicalRange({
      from: range.from + delta,
      to: range.to,
    });
  };

  const handleZoomOut = () => {
    if (!chartRef.current) return;
    const range = chartRef.current.timeScale().getVisibleLogicalRange();
    if (!range) return;
    const barsCount = range.to - range.from;
    const delta = Math.max(2, Math.floor(barsCount * 0.2));
    chartRef.current.timeScale().setVisibleLogicalRange({
      from: Math.max(0, range.from - delta),
      to: range.to + (delta / 2),
    });
  };

  return (
    <div className="relative w-full h-[420px] group">
      <div ref={chartContainerRef} className="w-full h-full rounded-xl overflow-hidden" />

      {/* Floating Interactive Controls Toolbar */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 bg-slate-900/80 backdrop-blur-md px-2 py-1 rounded-xl border border-slate-800 shadow-lg">
        <button
          onClick={handleResetToLatest}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-mono font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          title="Reset to latest candles"
        >
          <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
          <span>Latest</span>
        </button>
        <button
          onClick={handleFitAll}
          className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-mono font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          title="Fit all candles on screen"
        >
          <Maximize2 className="w-3.5 h-3.5 text-cyan-400" />
          <span>Fit All</span>
        </button>
        <div className="w-[1px] h-4 bg-slate-800 my-auto" />
        <button
          onClick={handleZoomIn}
          className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          title="Zoom In"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          title="Zoom Out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Subtle Drag & Zoom Helper Hint */}
      <div className="absolute bottom-2 left-3 z-10 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800 shadow">
          <Compass className="w-3 h-3 text-cyan-400" />
          <span>Drag horizontally to pan historical data • Scroll wheel to zoom</span>
        </div>
      </div>

      {candles.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/60 rounded-xl">
          <span className="text-sm text-slate-400">Loading {symbol} real market data...</span>
        </div>
      )}
    </div>
  );
};
