import React, { lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './layouts/MainLayout';
import { useAppStore } from './store/useAppStore';

const Overview = lazy(() => import('./pages/Overview').then((m) => ({ default: m.Overview })));
const MarketExplorer = lazy(() => import('./pages/MarketExplorer').then((m) => ({ default: m.MarketExplorer })));
const AssetDetails = lazy(() => import('./pages/AssetDetails').then((m) => ({ default: m.AssetDetails })));
const NewsSentiment = lazy(() => import('./pages/NewsSentiment').then((m) => ({ default: m.NewsSentiment })));
const AIInsights = lazy(() => import('./pages/AIInsights').then((m) => ({ default: m.AIInsights })));
const StrategyBuilder = lazy(() => import('./pages/StrategyBuilder').then((m) => ({ default: m.StrategyBuilder })));
const Backtesting = lazy(() => import('./pages/Backtesting').then((m) => ({ default: m.Backtesting })));
const PortfolioSimulator = lazy(() => import('./pages/PortfolioSimulator').then((m) => ({ default: m.PortfolioSimulator })));
const PerformanceAnalytics = lazy(() => import('./pages/PerformanceAnalytics').then((m) => ({ default: m.PerformanceAnalytics })));
const Settings = lazy(() => import('./pages/Settings').then((m) => ({ default: m.Settings })));

const PageLoader: React.FC = () => (
  <div className="flex h-96 w-full flex-col items-center justify-center space-y-4">
    <div className="h-10 w-10 animate-spin rounded-full border-2 border-emerald-500/20 border-t-emerald-500" />
    <span className="text-xs font-mono uppercase tracking-widest text-slate-400">
      Loading Module...
    </span>
  </div>
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5000,
    },
  },
});

const ContentSwitcher: React.FC = () => {
  const activeTab = useAppStore((s) => s.activeTab);

  return (
    <Suspense fallback={<PageLoader />}>
      {(() => {
        switch (activeTab) {
          case 'overview':
            return <Overview />;
          case 'market-explorer':
            return <MarketExplorer />;
          case 'asset-details':
            return <AssetDetails />;
          case 'news-sentiment':
            return <NewsSentiment />;
          case 'ai-insights':
            return <AIInsights />;
          case 'strategy-builder':
            return <StrategyBuilder />;
          case 'backtesting':
            return <Backtesting />;
          case 'portfolio-simulator':
            return <PortfolioSimulator />;
          case 'performance-analytics':
            return <PerformanceAnalytics />;
          case 'settings':
            return <Settings />;
          default:
            return <Overview />;
        }
      })()}
    </Suspense>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainLayout>
        <ContentSwitcher />
      </MainLayout>
    </QueryClientProvider>
  );
}
