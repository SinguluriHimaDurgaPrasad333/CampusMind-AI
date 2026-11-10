import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  GraduationCap,
  Sparkles,
  MessageSquare,
  BookOpen,
  Shield,
  BarChart3,
  Sun,
  Moon,
  Activity,
  Menu,
  X
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { api } from '../services/api';

export const Navbar = () => {
  const { isDark, toggleTheme } = useTheme();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    api.getHealth()
      .then(res => setHealthStatus(res.status))
      .catch(() => setHealthStatus('degraded'));
  }, []);

  const navLinks = [
    { name: 'Assistant', path: '/chat', icon: MessageSquare },
    { name: 'Knowledge Base', path: '/knowledge-base', icon: BookOpen },
    { name: 'Analytics & Eval', path: '/analytics', icon: BarChart3 },
    { name: 'Admin Portal', path: '/admin', icon: Shield },
  ];

  return (
    <nav className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/60 dark:border-white/10 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-aurora-cyan via-aurora-blue to-aurora-purple p-0.5 shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all duration-300">
              <div className="w-full h-full bg-space-900 rounded-[10px] flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-aurora-cyan group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent dark:from-white dark:to-slate-300">
                  CampusMind
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-md bg-aurora-cyan/20 text-aurora-cyan border border-aurora-cyan/30 uppercase tracking-wider">
                  AI RAG
                </span>
              </div>
              <p className="text-[10px] text-slate-400 dark:text-slate-400 hidden sm:block">
                Intelligent University Student Assistant
              </p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-slate-800/80 dark:bg-white/10 text-aurora-cyan shadow-sm border border-cyan-500/30'
                      : 'text-slate-300 dark:text-slate-300 hover:text-white hover:bg-slate-800/40 dark:hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-aurora-cyan' : 'text-slate-400'}`} />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </div>

          {/* Right Action Icons */}
          <div className="flex items-center space-x-3">
            {/* Live Status indicator */}
            <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 dark:bg-black/40 border border-slate-700/50 text-[11px] font-mono">
              <span className={`w-2 h-2 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="text-slate-300 dark:text-slate-300">
                {healthStatus === 'healthy' ? 'RAG Engine Online' : 'Connecting'}
              </span>
            </div>

            {/* Dark / Light Toggle */}
            <button
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 dark:hover:bg-white/10 transition-colors"
            >
              {isDark ? <Sun className="w-5 h-5 text-amber-300" /> : <Moon className="w-5 h-5 text-indigo-600" />}
            </button>

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel border-b border-slate-800 px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive
                    ? 'bg-aurora-cyan/20 text-aurora-cyan border border-aurora-cyan/30'
                    : 'text-slate-300 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-4 h-4 text-aurora-cyan" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>
      )}
    </nav>
  );
};
