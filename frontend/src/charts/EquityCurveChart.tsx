import React, { useMemo } from 'react';
import type { EquityPoint } from '../types';

interface EquityCurveChartProps {
  equityCurve: EquityPoint[];
  initialCapital: number;
  benchmarkReturn?: number;
}

export const EquityCurveChart: React.FC<EquityCurveChartProps> = ({
  equityCurve,
  initialCapital,
  benchmarkReturn
}) => {
  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="h-64 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-center font-mono text-xs text-slate-500">
        No simulation data available. Click "Run Backtest" to generate equity curve.
      </div>
    );
  }

  const { points, minEq, maxEq, benchmarkFinal } = useMemo(() => {
    let min = Infinity;
    let max = -Infinity;

    equityCurve.forEach((pt) => {
      if (pt.equity < min) min = pt.equity;
      if (pt.equity > max) max = pt.equity;
    });

    const benchFinal = benchmarkReturn !== undefined ? initialCapital * (1.0 + benchmarkReturn) : undefined;
    if (benchFinal !== undefined) {
      if (benchFinal < min) min = benchFinal;
      if (benchFinal > max) max = benchFinal;
    }

    // Add 2% padding
    const padding = (max - min) * 0.05 || 1000;
    min -= padding;
    max += padding;

    return {
      points: equityCurve,
      minEq: min,
      maxEq: max,
      benchmarkFinal: benchFinal,
    };
  }, [equityCurve, initialCapital, benchmarkReturn]);

  const width = 800;
  const height = 240;
  const padLeft = 60;
  const padRight = 20;
  const padTop = 20;
  const padBottom = 30;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const getX = (index: number) => {
    return padLeft + (index / (points.length - 1 || 1)) * chartW;
  };

  const getY = (val: number) => {
    const range = maxEq - minEq || 1;
    return padTop + chartH - ((val - minEq) / range) * chartH;
  };

  // Generate SVG path for Equity
  const pathD = points.reduce((acc, pt, i) => {
    const x = getX(i);
    const y = getY(pt.equity);
    return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, '');

  // Generate closed area path for gradient
  const areaD = `${pathD} L ${getX(points.length - 1)} ${getY(minEq)} L ${getX(0)} ${getY(minEq)} Z`;

  // Benchmark line from initial to final
  const benchPathD = benchmarkFinal !== undefined
    ? `M ${getX(0)} ${getY(initialCapital)} L ${getX(points.length - 1)} ${getY(benchmarkFinal)}`
    : '';

  // Y-axis ticks
  const yTicks = [
    maxEq,
    minEq + (maxEq - minEq) * 0.75,
    minEq + (maxEq - minEq) * 0.5,
    minEq + (maxEq - minEq) * 0.25,
    minEq,
  ];

  return (
    <div className="w-full relative">
      <div className="flex items-center justify-between text-xs text-slate-400 mb-2 px-1">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span className="font-mono text-slate-300">Strategy Equity</span>
          </div>
          {benchmarkFinal !== undefined && (
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-0.5 bg-slate-400 border border-dashed border-slate-400"></span>
              <span className="font-mono text-slate-400">Buy & Hold Benchmark</span>
            </div>
          )}
        </div>
        <div className="font-mono text-[11px] text-slate-400">
          Range: ${minEq.toLocaleString(undefined, { maximumFractionDigits: 0 })} – ${maxEq.toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </div>
      </div>

      <div className="w-full overflow-hidden rounded-xl bg-slate-950/90 border border-slate-800 p-2">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-56 sm:h-64"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {yTicks.map((tick, i) => {
            const y = getY(tick);
            return (
              <g key={i}>
                <line
                  x1={padLeft}
                  y1={y}
                  x2={width - padRight}
                  y2={y}
                  stroke="#1e293b"
                  strokeDasharray="4 4"
                />
                <text
                  x={padLeft - 6}
                  y={y + 3}
                  textAnchor="end"
                  fill="#64748b"
                  fontSize="9"
                  fontFamily="monospace"
                >
                  ${(tick / 1000).toFixed(0)}k
                </text>
              </g>
            );
          })}

          {/* Gradient area under equity curve */}
          <path d={areaD} fill="url(#equityGrad)" />

          {/* Benchmark line */}
          {benchPathD && (
            <path
              d={benchPathD}
              fill="none"
              stroke="#64748b"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
          )}

          {/* Equity line */}
          <path
            d={pathD}
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Start and end points */}
          {points.length > 0 && (
            <>
              <circle
                cx={getX(0)}
                cy={getY(points[0].equity)}
                r="3"
                fill="#10b981"
              />
              <circle
                cx={getX(points.length - 1)}
                cy={getY(points[points.length - 1].equity)}
                r="4"
                fill="#10b981"
                stroke="#020617"
                strokeWidth="2"
              />
            </>
          )}
        </svg>
      </div>
    </div>
  );
};

