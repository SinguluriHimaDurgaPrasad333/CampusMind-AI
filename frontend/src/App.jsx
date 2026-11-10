import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { ChatProvider } from './context/ChatContext';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { ChatPage } from './pages/ChatPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { AdminPage } from './pages/AdminPage';
import { AnalyticsPage } from './pages/AnalyticsPage';

function AppContent() {
  const location = useLocation();
  // Hide top navbar on the ChatGPT interface for a true full-screen ChatGPT look
  const isChatOnly = location.pathname === '/' || location.pathname === '/chat';

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0c14] text-slate-100 selection:bg-cyan-500/30 selection:text-white transition-colors duration-200">
      {!isChatOnly && <Navbar />}
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/about" element={<LandingPage />} />
          <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}

export function App() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <Router>
          <AppContent />
        </Router>
      </ChatProvider>
    </ThemeProvider>
  );
}

export default App;
