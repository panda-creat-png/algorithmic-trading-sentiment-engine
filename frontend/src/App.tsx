import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './layouts/MainLayout';
import { useAppStore } from './store/useAppStore';

import { Overview } from './pages/Overview';
import { MarketExplorer } from './pages/MarketExplorer';
import { AssetDetails } from './pages/AssetDetails';
import { NewsSentiment } from './pages/NewsSentiment';
import { AIInsights } from './pages/AIInsights';
import { StrategyBuilder } from './pages/StrategyBuilder';
import { Backtesting } from './pages/Backtesting';
import { PortfolioSimulator } from './pages/PortfolioSimulator';
import { PerformanceAnalytics } from './pages/PerformanceAnalytics';
import { Settings } from './pages/Settings';

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
