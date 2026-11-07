import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Play, Sliders, ShieldCheck, Cpu } from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import type { Strategy } from '../types';

export const StrategyBuilder: React.FC = () => {
  const { setActiveTab } = useAppStore();

  const { data: strategies, isLoading } = useQuery({
    queryKey: ['strategies-list'],
    queryFn: api.getStrategies,
    staleTime: 60000,
  });

  const FALLBACK_STRATEGIES: Partial<Strategy>[] = [
    {
      id: 1,
      name: 'Dual Moving Average Crossover',
      strategy_type: 'ma_crossover',
      description: 'Golden Cross / Death Cross with 20 & 50 period SMA with ATR dynamic trailing stop.',
      parameters: { fast_period: 20, slow_period: 50, stop_loss_pct: 0.02, take_profit_pct: 0.05 },
      is_active: true,
    },
    {
      id: 2,
      name: 'RSI Mean Reversion',
      strategy_type: 'rsi_reversal',
      description: 'Enters long on oversold RSI (<30) and takes profit on overbought RSI (>70).',
      parameters: { rsi_period: 14, oversold: 30, overbought: 70 },
      is_active: true,
    },
    {
      id: 3,
      name: 'MACD Momentum Trend',
      strategy_type: 'macd',
      description: 'Enters trades when MACD histogram crosses zero line with confirmation.',
      parameters: { fast: 12, slow: 26, signal: 9 },
      is_active: true,
    },
    {
      id: 4,
      name: 'Bollinger Bands Volatility Breakout',
      strategy_type: 'bollinger',
      description: 'Trades price channel breakouts and standard deviation squeezes.',
      parameters: { period: 20, std_dev: 2.0 },
      is_active: true,
    },
    {
      id: 5,
      name: 'Momentum Breakout Strategy',
      strategy_type: 'momentum',
      description: 'Trades Rate of Change (ROC) price acceleration breakouts above threshold.',
      parameters: { lookback: 14, threshold: 0.02 },
      is_active: true,
    },
    {
      id: 6,
      name: 'FinBERT AI Sentiment Strategy',
      strategy_type: 'sentiment',
      description: 'Executes long/short positions exclusively on high-conviction FinBERT news sentiment spikes.',
      parameters: { sentiment_threshold: 0.65, min_confidence: 0.70 },
      is_active: true,
    },
    {
      id: 7,
      name: 'AI Sentiment Augmented Momentum',
      strategy_type: 'combined',
      description: 'Combines RSI momentum signals with FinBERT news sentiment confirmation score.',
      parameters: { sentiment_threshold: 0.65, rsi_threshold: 50, rsi_period: 14 },
      is_active: true,
    },
  ];

  const strategyList = strategies && strategies.length > 0 ? strategies : FALLBACK_STRATEGIES;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">Algorithmic Strategy Builder</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              7 Modular Strategies
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Modular quantitative strategy framework with zero look-ahead bias execution models.
          </p>
        </div>

        <button
          onClick={() => setActiveTab('backtesting')}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-emerald-500/10 active:scale-95"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Launch Backtest</span>
        </button>
      </div>

      {/* Architecture Alert */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <span className="font-bold text-emerald-400">Modular Strategy Architecture</span>
          <p className="text-slate-400 leading-relaxed">
            Every strategy inherits from BaseStrategy and emits vectorized signals via Polars. All strategies are decoupled from the event-driven simulation engine, allowing new quantitative models to be added seamlessly.
          </p>
        </div>
      </div>

      {/* Strategies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {isLoading ? (
          <div className="col-span-2 p-12 text-center text-slate-500 font-mono text-xs">
            Loading quantitative strategies...
          </div>
        ) : (
          strategyList.map((strat) => (
            <div
              key={strat.id}
              className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all shadow-md"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-bold text-white">{strat.name}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    {strat.strategy_type}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                  {strat.description}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <Sliders className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  {strat.parameters &&
                    Object.entries(strat.parameters).map(([k, v]) => (
                      <span
                        key={k}
                        className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-300"
                      >
                        {k}: <strong className="text-emerald-400">{String(v)}</strong>
                      </span>
                    ))}
                </div>
                <button
                  onClick={() => setActiveTab('backtesting')}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors shrink-0"
                >
                  Configure & Test
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
