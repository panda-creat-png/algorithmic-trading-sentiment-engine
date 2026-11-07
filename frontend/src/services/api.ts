import axios from 'axios';
import type {
  HealthResponse,
  Asset,
  MarketHistory,
  NewsArticle,
  MarketSentimentOverview,
  SentimentAnalysisResult,
  Strategy,
  BacktestRun,
  PortfolioOverview,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const api = {
  // System Health
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get<HealthResponse>('/health');
    return res.data;
  },

  // Market
  getAssets: async (): Promise<Asset[]> => {
    const res = await apiClient.get<Asset[]>('/market/assets');
    return res.data;
  },

  getQuote: async (symbol: string): Promise<any> => {
    const res = await apiClient.get(`/market/${symbol}/quote`);
    return res.data;
  },

  getMarketHistory: async (symbol: string, timeframe = '1d', limit = 100): Promise<MarketHistory> => {
    const res = await apiClient.get<MarketHistory>(`/market/${symbol}/history`, {
      params: { timeframe, limit },
    });
    return res.data;
  },

  getTechnicalIndicators: async (symbol: string, timeframe = '1d', limit = 60): Promise<any> => {
    const res = await apiClient.get(`/market/${symbol}/indicators`, {
      params: { timeframe, limit },
    });
    return res.data;
  },

  getSentimentCorrelation: async (symbol: string, timeframe = '1d'): Promise<any> => {
    const res = await apiClient.get(`/ai/correlation/${symbol}`, {
      params: { timeframe },
    });
    return res.data;
  },

  syncNews: async (symbols?: string[]): Promise<any> => {
    const res = await apiClient.post('/news/sync', symbols ? { symbols } : {});
    return res.data;
  },

  // News & AI Sentiment
  getNews: async (symbol?: string, limit = 20): Promise<NewsArticle[]> => {
    const res = await apiClient.get<NewsArticle[]>('/news', {
      params: { symbol, limit },
    });
    return res.data;
  },

  getMarketSentiment: async (): Promise<MarketSentimentOverview> => {
    const res = await apiClient.get<MarketSentimentOverview>('/news/sentiment');
    return res.data;
  },

  analyzeSentiment: async (text: string, symbol?: string): Promise<SentimentAnalysisResult> => {
    const res = await apiClient.post<SentimentAnalysisResult>('/ai/analyze', { text, symbol });
    return res.data;
  },

  // Strategies
  getStrategies: async (): Promise<Strategy[]> => {
    const res = await apiClient.get<Strategy[]>('/strategies');
    return res.data;
  },

  createStrategy: async (data: Partial<Strategy>): Promise<Strategy> => {
    const res = await apiClient.post<Strategy>('/strategies', data);
    return res.data;
  },

  // Backtests
  runBacktest: async (payload: any): Promise<BacktestRun> => {
    const res = await apiClient.post<BacktestRun>('/backtests/run', payload);
    return res.data;
  },

  getBacktests: async (): Promise<BacktestRun[]> => {
    const res = await apiClient.get<BacktestRun[]>('/backtests');
    return res.data;
  },

  // Portfolio
  getPortfolio: async (): Promise<PortfolioOverview> => {
    const res = await apiClient.get<PortfolioOverview>('/portfolio');
    return res.data;
  },

  executePaperOrder: async (data: { symbol: string; side: 'buy' | 'sell'; quantity: number }): Promise<PortfolioOverview> => {
    const res = await apiClient.post<PortfolioOverview>('/portfolio/order', data);
    return res.data;
  },

  resetPortfolio: async (): Promise<PortfolioOverview> => {
    const res = await apiClient.post<PortfolioOverview>('/portfolio/reset');
    return res.data;
  },
};

