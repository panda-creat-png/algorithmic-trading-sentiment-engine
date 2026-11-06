// QuantMind AI - TypeScript Domain Interfaces

export type AssetClass = 'stock' | 'crypto' | 'forex';
export type SentimentType = 'positive' | 'negative' | 'neutral';
export type StrategyType = 
  | 'ma_crossover'
  | 'rsi_reversal'
  | 'macd'
  | 'bollinger'
  | 'momentum'
  | 'sentiment'
  | 'combined';

export interface Asset {
  id: number;
  symbol: string;
  name: string;
  asset_class: AssetClass;
  exchange: string;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  trades_count?: number;
  vwap?: number;
}

export interface MarketHistory {
  symbol: string;
  timeframe: string;
  total_candles: number;
  candles: Candle[];
}

export interface NewsArticle {
  id: number;
  title: string;
  url?: string;
  source: string;
  summary?: string;
  content?: string;
  published_at: string;
  author?: string;
}

export interface SentimentAnalysisResult {
  headline: string;
  symbol?: string;
  sentiment: SentimentType;
  positive_score: number;
  negative_score: number;
  neutral_score: number;
  confidence: number;
  relevance_score: number;
  model_name: string;
}

export interface MarketSentimentOverview {
  bullish_index: number;
  bearish_index: number;
  neutral_index: number;
  overall_sentiment: string;
  sentiment_trend: string;
  analyzed_headlines_count: number;
}

export interface Strategy {
  id: number;
  name: string;
  description?: string;
  strategy_type: StrategyType;
  is_active: boolean;
  parameters: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface BacktestMetrics {
  total_return?: number;
  cagr?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  max_drawdown?: number;
  calmar_ratio?: number;
  win_rate?: number;
  profit_factor?: number;
  total_trades: number;
  annualized_volatility?: number;
  exposure_time?: number;
  benchmark_return?: number;
}

export interface BacktestRun {
  id: number;
  strategy_id: number;
  asset_id: number;
  symbol?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_date: string;
  end_date: string;
  timeframe: string;
  initial_capital: number;
  final_equity?: number;
  metrics: BacktestMetrics;
  error_message?: string;
  created_at: string;
}

export interface Position {
  symbol: string;
  quantity: number;
  average_entry_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

export interface PortfolioOverview {
  total_equity: number;
  cash_balance: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_return_pct: number;
  positions: Position[];
  timestamp: string;
}

export interface ServiceStatus {
  status: string;
  latency_ms?: number;
  database_type?: string;
  backend?: string;
  note?: string;
  error?: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'critical';
  timestamp: string;
  version: string;
  environment: string;
  database: ServiceStatus;
  redis: ServiceStatus;
  meta: Record<string, any>;
}

export type NavTab = 
  | 'overview'
  | 'market-explorer'
  | 'asset-details'
  | 'news-sentiment'
  | 'ai-insights'
  | 'strategy-builder'
  | 'backtesting'
  | 'portfolio-simulator'
  | 'performance-analytics'
  | 'settings';

