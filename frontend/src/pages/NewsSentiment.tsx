import React, { useState } from 'react';
import { Sparkles, Send } from 'lucide-react';
import { api } from '../services/api';
import type { SentimentAnalysisResult } from '../types';

export const NewsSentiment: React.FC = () => {
  const [inputText, setInputText] = useState<string>('');
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<SentimentAnalysisResult | null>(null);

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

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-white">News & AI Financial Sentiment Engine</h1>
        <p className="text-sm text-slate-400">
          FinBERT NLP pipeline with entity extraction, sentiment scoring, and historical price correlation.
        </p>
      </div>

      {/* Live AI Inference Tester */}
      <div className="p-5 rounded-2xl bg-[#0c1224] border border-slate-800 shadow-md">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <h2 className="font-bold text-white text-sm">FinBERT Interactive Sentiment Inference Test</h2>
        </div>

        <form onSubmit={handleTestInference} className="mt-4 space-y-3">
          <textarea
            rows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter any financial headline or earnings release text (e.g. 'Company reports record revenue and exceeds Q3 consensus estimates with surging demand')..."
            className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-500">Model: ProsusAI/finbert (PyTorch / Transformers)</span>
            <button
              type="submit"
              disabled={analyzing || !inputText.trim()}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all"
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
                className={`font-bold uppercase px-2 py-0.5 rounded ${
                  result.sentiment === 'positive'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : result.sentiment === 'negative'
                    ? 'bg-rose-500/20 text-rose-400'
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
            <div className="text-[11px] text-slate-500 pt-1">
              Confidence: {(result.confidence * 100).toFixed(1)}% | Relevance Score: {result.relevance_score}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
