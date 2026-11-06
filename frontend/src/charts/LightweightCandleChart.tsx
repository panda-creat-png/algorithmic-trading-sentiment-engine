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
      },
      rightPriceScale: {
        borderColor: '#1e293b',
        autoScale: true,
      },
      handleScale: {
        mouseWheel: true,
        pinch: true,
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
      chartRef.current?.timeScale().fitContent();
    } catch (err) {
      console.warn('Error rendering candles in chart:', err);
    }
  }, [candles]);

  return (
    <div className="relative w-full h-[400px]">
      <div ref={chartContainerRef} className="w-full h-full rounded-xl overflow-hidden" />
      {candles.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/60 rounded-xl">
          <span className="text-sm text-slate-400">Loading {symbol} real market data...</span>
        </div>
      )}
    </div>
  );
};

