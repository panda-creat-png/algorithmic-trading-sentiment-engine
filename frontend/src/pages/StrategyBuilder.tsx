import React from 'react';
import { Play } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export const StrategyBuilder: React.FC = () => {
  const { setActiveTab } = useAppStore();

  const STRATEGIES = [
    {
      id: 1,
      name: 'Dual Moving Average Crossover',
      type: 'ma_crossover',
      desc: 'Golden Cross / Death Cross with 20 & 50 period SMA with ATR dynamic trailing stop.',
      params: 'Fast: 20, Slow: 50, SL: 2%, TP: 5%',
      status: 'Active',
    },
    {
      id: 2,
      name: 'RSI Mean Reversion',
      type: 'rsi_reversal',
      desc: 'Enters long on oversold RSI (<30) and takes profit on overbought RSI (>70).',
      params: 'Period: 14, Oversold: 30, Overbought: 70',
      status: 'Active',
    },
    {
      id: 3,
      name: 'MACD Momentum Trend',
      type: 'macd',
      desc: 'Zero-line crossover confirmation with volume filter.',
      params: 'Fast: 12, Slow: 26, Signal: 9',
      status: 'Active',
    },
    {
      id: 4,
      name: 'Bollinger Bands Volatility Breakout',
      type: 'bollinger',
      desc: 'Enters breakouts outside 2.0 std deviations during volatility contraction.',
      params: 'Period: 20, StdDev: 2.0',
      status: 'Active',
    },
    {
      id: 5,
      name: 'AI Sentiment-Based Augmented Strategy',
      type: 'combined',
      desc: 'Executes trades only when technical signals are confirmed by positive FinBERT news scores.',
      params: 'FinBERT Threshold: 0.70, Technical Weight: 0.5',
      status: 'Active',
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">Algorithmic Strategy Builder</h1>
          <p className="text-sm text-slate-400">
            Design, calibrate, and parameterize institutional quantitative trading strategies.
          </p>
        </div>

        <button
          onClick={() => setActiveTab('backtesting')}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-emerald-500/10"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Launch Backtest</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {STRATEGIES.map((strat) => (
          <div key={strat.id} className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white">{strat.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  {strat.type}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-2">{strat.desc}</p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">{strat.params}</span>
              <button
                onClick={() => setActiveTab('backtesting')}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-sans font-semibold transition-colors"
              >
                Backtest Strategy
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
