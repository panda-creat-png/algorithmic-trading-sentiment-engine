import React from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { TopNavbar } from '../components/layout/TopNavbar';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#080d1a] text-slate-100 font-sans">
      <Sidebar />
      <div className="flex flex-col flex-1 h-screen overflow-hidden">
        <TopNavbar />
        <main className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-[#090e1c] to-[#070b16]">
          {children}
        </main>
      </div>
    </div>
  );
};

