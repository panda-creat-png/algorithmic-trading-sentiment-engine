import { create } from 'zustand';
import type { NavTab, HealthResponse } from '../types';

interface AppUser {
  id: number;
  email: string;
  full_name?: string;
  is_superuser?: boolean;
}

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

  currentUser: AppUser | null;
  authToken: string | null;
  loginUser: (user: AppUser, token: string) => void;
  logoutUser: () => void;
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

  currentUser: (() => {
    try {
      const u = localStorage.getItem('quantmind_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  })(),
  authToken: localStorage.getItem('quantmind_token') || null,
  loginUser: (user, token) => {
    localStorage.setItem('quantmind_token', token);
    localStorage.setItem('quantmind_user', JSON.stringify(user));
    set({ currentUser: user, authToken: token });
  },
  logoutUser: () => {
    localStorage.removeItem('quantmind_token');
    localStorage.removeItem('quantmind_user');
    set({ currentUser: null, authToken: null });
  },
}));

