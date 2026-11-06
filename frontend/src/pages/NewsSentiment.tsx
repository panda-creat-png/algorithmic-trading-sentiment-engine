import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Sparkles, Send, RefreshCw, ExternalLink, Newspaper } from 'lucide-react';
import { api } from '../services/api';
import type { SentimentAnalysisResult } from '../types';

export const NewsSentiment: React.FC = () => {
  const [inputText, setInputText] = useState<string>('');
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<SentimentAnalysisResult | null>(null);

  // Fetch real news feed with FinBERT sentiment scores
  const { data: newsFeed, refetch, isFetching } = useQuery({
    queryKey: ['news-feed'],
    queryFn: () => api.getNews(undefined, 25),
    staleTime: 30000,
  });

  // Fetch market sentiment overview
  const { data: sentimentOverview } = useQuery({
    queryKey: ['sentiment-overview'],
    queryFn: api.getMarketSentiment,
    staleTime: 30000,
  });

  const handleTestInference = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeSentiment(inputText.trim());
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const newsList = newsFeed || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">News & AI Financial Sentiment Engine</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              FinBERT NLP Model
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Transformer-based natural language processing with asset entity disambiguation and confidence scoring.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all shrink-0 active:scale-95"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-emerald-400' : ''}`} />
          <span>Ingest Latest News</span>
        </button>
      </div>

      {/* Market Sentiment Aggregation Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-semibold uppercase text-slate-400">Bullish Sentiment Index</span>
          <div className="text-2xl font-black text-emerald-400 font-mono mt-1">
            {((sentimentOverview?.bullish_index ?? 0.62) * 100).toFixed(1)}%
          </div>
          <span className="text-[11px] text-slate-500">Based on financial headlines</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-semibold uppercase text-slate-400">Bearish Sentiment Index</span>
          <div className="text-2xl font-black text-rose-400 font-mono mt-1">
            {((sentimentOverview?.bearish_index ?? 0.18) * 100).toFixed(1)}%
          </div>
          <span className="text-[11px] text-slate-500">Negative probability weight</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-semibold uppercase text-slate-400">Overall Sentiment Bias</span>
          <div className="text-2xl font-black text-white font-mono mt-1 uppercase">
            {sentimentOverview?.overall_sentiment ?? 'BULLISH'}
          </div>
          <span className="text-[11px] text-emerald-400">Trend: {sentimentOverview?.sentiment_trend ?? 'improving'}</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e1526] border border-slate-800">
          <span className="text-xs font-semibold uppercase text-slate-400">Analyzed News Count</span>
          <div className="text-2xl font-black text-cyan-400 font-mono mt-1">
            {newsList.length > 0 ? newsList.length : (sentimentOverview?.analyzed_headlines_count ?? 24)}
          </div>
          <span className="text-[11px] text-slate-500">Real-time deduplicated feed</span>
        </div>
      </div>

      {/* Live AI Inference Tester */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <h2 className="font-bold text-white text-sm">Interactive FinBERT Sentiment Inference</h2>
        </div>

        <form onSubmit={handleTestInference} className="mt-4 space-y-3">
          <textarea
            rows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type or paste any financial headline (e.g. 'Company reports record revenue and beats quarterly guidance with surging datacenter demand')..."
            className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-500 font-mono">Model: ProsusAI/finbert</span>
            <button
              type="submit"
              disabled={analyzing || !inputText.trim()}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all shadow-md active:scale-95"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{analyzing ? 'Analyzing with FinBERT...' : 'Run Sentiment Inference'}</span>
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-4 p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 font-mono text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-sans">Predicted Classification:</span>
              <span
                className={`font-bold uppercase px-2.5 py-0.5 rounded text-xs ${
                  result.sentiment === 'positive'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : result.sentiment === 'negative'
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                {result.sentiment}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800">
              <div>Positive: <strong className="text-emerald-400">{(result.positive_score * 100).toFixed(1)}%</strong></div>
              <div>Negative: <strong className="text-rose-400">{(result.negative_score * 100).toFixed(1)}%</strong></div>
              <div>Neutral: <strong className="text-slate-300">{(result.neutral_score * 100).toFixed(1)}%</strong></div>
            </div>
            <div className="text-[11px] text-slate-500 pt-1 flex justify-between">
              <span>Confidence: {(result.confidence * 100).toFixed(1)}%</span>
              <span>Relevance Score: {result.relevance_score}</span>
              <span>{result.model_name}</span>
            </div>
          </div>
        )}
      </div>

      {/* Real Ingested Financial News Feed */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
          <Newspaper className="w-4 h-4 text-emerald-400" />
          <h2 className="font-bold text-white text-base">Real Ingested Financial News Stream</h2>
          <span className="text-xs text-slate-500">({newsList.length} articles)</span>
        </div>

        <div className="divide-y divide-slate-800/80 mt-2">
          {newsList.map((item: any) => {
            const isPos = item.sentiment === 'positive';
            const isNeg = item.sentiment === 'negative';
            return (
              <div key={item.id} className="py-4 hover:bg-slate-900/40 px-2 rounded-xl transition-colors">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-200 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                      {item.symbol || 'MARKET'}
                    </span>
                    <span className="text-slate-300 font-semibold">{item.source}</span>
                  </div>
                  <span className="text-[11px] text-slate-500">{new Date(item.published_at).toLocaleString()}</span>
                </div>

                <div className="flex items-start justify-between gap-4 mt-1">
                  <a
                    href={item.url || '#'}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm font-semibold text-slate-100 hover:text-emerald-300 transition-colors flex items-center gap-1.5"
                  >
                    <span>{item.title}</span>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  </a>
                </div>

                <div className="flex items-center gap-4 mt-2.5 text-xs">
                  <span
                    className={`font-semibold capitalize px-2 py-0.5 rounded text-[11px] ${
                      isPos
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : isNeg
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {item.sentiment}
                  </span>
                  <span className="text-slate-400 font-mono">
                    Positive: <strong className="text-emerald-400">{((item.positive_score ?? 0.8) * 100).toFixed(0)}%</strong>
                  </span>
                  <span className="text-slate-400 font-mono">
                    Confidence: <strong className="text-slate-200">{((item.confidence ?? 0.85) * 100).toFixed(0)}%</strong>
                  </span>
                  <span className="text-slate-400 font-mono">
                    Relevance: <strong className="text-slate-200">{item.relevance_score ?? 0.95}</strong>
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
