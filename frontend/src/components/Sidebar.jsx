import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Plus,
  MessageSquare,
  Trash2,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Shield,
  BarChart3,
  Search,
  Sparkles,
  Info,
  User,
  GraduationCap
} from 'lucide-react';
import { useChat } from '../context/ChatContext';

export const Sidebar = ({ isCollapsed, setIsCollapsed }) => {
  const {
    sessions,
    activeSessionId,
    setActiveSessionId,
    startNewChat,
    deleteSession
  } = useChat();

  const [searchTerm, setSearchTerm] = useState('');
  const location = useLocation();

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <aside
      className={`relative flex flex-col h-full bg-[#0d0f17] border-r border-white/5 transition-all duration-300 z-30 select-none ${
        isCollapsed ? 'w-16' : 'w-72 sm:w-80'
      }`}
    >
      {/* Top Header: Brand & New Chat */}
      <div className="p-3 border-b border-white/5 space-y-2">
        <div className="flex items-center justify-between">
          <Link to="/" onClick={startNewChat} className="flex items-center space-x-2.5 overflow-hidden group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-aurora-cyan via-aurora-blue to-aurora-purple p-0.5 flex-shrink-0 shadow-md shadow-cyan-500/20">
              <div className="w-full h-full bg-space-950 rounded-[6px] flex items-center justify-center">
                <GraduationCap className="w-4 h-4 text-aurora-cyan" />
              </div>
            </div>
            {!isCollapsed && (
              <div className="truncate">
                <div className="flex items-center space-x-1.5">
                  <span className="font-extrabold text-sm text-white">CampusMind</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    4.0
                  </span>
                </div>
              </div>
            )}
          </Link>

          {/* Collapse Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* New Chat Button */}
        <button
          onClick={startNewChat}
          className={`w-full flex items-center justify-center space-x-2 py-2.5 px-3 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium text-xs border border-white/10 hover:border-cyan-500/40 shadow-sm transition-all duration-200 group ${
            isCollapsed ? 'px-0' : ''
          }`}
          title="New conversation"
        >
          <Plus className="w-4 h-4 text-aurora-cyan group-hover:scale-110 transition-transform" />
          {!isCollapsed && <span>New Chat</span>}
        </button>

        {/* Search Input (Only when expanded) */}
        {!isCollapsed && sessions.length > 3 && (
          <div className="relative mt-2">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search chat history..."
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-black/40 border border-white/5 text-[11px] text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/40"
            />
          </div>
        )}
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {!isCollapsed && (
          <div className="px-2 py-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Conversations</span>
            <span className="text-[10px] bg-white/5 px-1.5 py-0.2 rounded text-slate-400">
              {sessions.length}
            </span>
          </div>
        )}

        {filteredSessions.length === 0 ? (
          !isCollapsed && (
            <div className="text-center py-8 px-4 text-xs text-slate-500">
              <MessageSquare className="w-6 h-6 mx-auto mb-1.5 opacity-30 text-aurora-cyan" />
              <p className="text-[11px]">No chats yet.</p>
              <p className="text-[10px] text-slate-600 mt-0.5">Start a new conversation!</p>
            </div>
          )
        ) : (
          filteredSessions.map((session) => {
            const isActive = activeSessionId === session.id;
            return (
              <div
                key={session.id}
                onClick={() => setActiveSessionId(session.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer text-xs transition-all duration-150 ${
                  isActive
                    ? 'bg-white/10 text-white font-medium border border-white/10 shadow-sm'
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                }`}
                title={session.title}
              >
                <div className="flex items-center space-x-2.5 overflow-hidden">
                  <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-aurora-cyan' : 'text-slate-500'}`} />
                  {!isCollapsed && (
                    <span className="truncate max-w-[170px] sm:max-w-[190px]">
                      {session.title}
                    </span>
                  )}
                </div>

                {!isCollapsed && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-red-400 transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Tools & Navigation */}
      <div className="p-2 border-t border-white/5 space-y-1">
        <Link
          to="/knowledge-base"
          className={`flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs transition-colors ${
            location.pathname === '/knowledge-base'
              ? 'bg-cyan-500/20 text-cyan-300 font-medium'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
          title="University Knowledge Base"
        >
          <BookOpen className="w-4 h-4 text-aurora-cyan flex-shrink-0" />
          {!isCollapsed && <span>Knowledge Base</span>}
        </Link>

        <Link
          to="/analytics"
          className={`flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs transition-colors ${
            location.pathname === '/analytics'
              ? 'bg-cyan-500/20 text-cyan-300 font-medium'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
          title="RAG Analytics & Evaluation"
        >
          <BarChart3 className="w-4 h-4 text-purple-400 flex-shrink-0" />
          {!isCollapsed && <span>Analytics & Benchmarks</span>}
        </Link>

        <Link
          to="/admin"
          className={`flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs transition-colors ${
            location.pathname === '/admin'
              ? 'bg-cyan-500/20 text-cyan-300 font-medium'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
          title="Admin Document Portal"
        >
          <Shield className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          {!isCollapsed && <span>Admin Portal</span>}
        </Link>

        {/* User Profile Footer */}
        <div className="pt-2 mt-1 border-t border-white/5">
          <div className="flex items-center space-x-2.5 px-2 py-1.5 rounded-xl hover:bg-white/5 text-xs text-slate-300">
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center font-bold text-white text-[11px] flex-shrink-0">
              U
            </div>
            {!isCollapsed && (
              <div className="truncate">
                <p className="text-xs font-semibold text-white truncate">Student User</p>
                <p className="text-[10px] text-slate-500 truncate">CampusMind Student Portal</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};
