import { create } from 'zustand';
import type { NavTab, HealthResponse } from '../types';

interface AppState {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  
  selectedSymbol: string;
  setSelectedSymbol: (symbol: string) => void;
  
  searchQuery: string;
  setSearchQuery: (query: string) => void;

  health: HealthResponse | null;
  setHealth: (health: HealthResponse | null) => void;
  
  isDarkTheme: boolean;
  toggleTheme: () => void;

  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'overview',
  setActiveTab: (tab) => set({ activeTab: tab }),

  selectedSymbol: 'NVDA',
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol.toUpperCase() }),

  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),

  health: null,
  setHealth: (health) => set({ health }),

  isDarkTheme: true,
  toggleTheme: () => set((state) => ({ isDarkTheme: !state.isDarkTheme })),

  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));

