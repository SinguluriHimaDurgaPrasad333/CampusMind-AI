import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  FileText,
  Clock,
  ShieldCheck,
  HelpCircle,
  ChevronDown,
  Compass,
  BookOpen,
  Sun,
  Moon,
  Paperclip
} from 'lucide-react';
import { useChat } from '../context/ChatContext';
import { useTheme } from '../context/ThemeContext';
import { Sidebar } from '../components/Sidebar';
import { SourceInspectorModal } from '../components/SourceInspectorModal';
import { FeedbackModal } from '../components/FeedbackModal';
import { StreamingMessage } from '../components/StreamingMessage';

export const ChatPage = () => {
  const {
    messages,
    isLoading,
    error,
    activeCitation,
    setActiveCitation,
    suggestions,
    sendMessage,
    rateMessage,
    startNewChat
  } = useChat();

  const { isDark, toggleTheme } = useTheme();

  const [input, setInput] = useState('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [feedbackTarget, setFeedbackTarget] = useState(null);
  const [streamingMessageId, setStreamingMessageId] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Track latest assistant message to stream it
  useEffect(() => {
    if (messages.length > 0) {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.role === 'assistant' && !lastMsg.id.startsWith('loaded-')) {
        setStreamingMessageId(lastMsg.id);
      }
    }
  }, [messages]);

  // Auto-resize textarea
  const handleInputChange = (e) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  const handleSend = (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;
    const queryToSend = input.trim();
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    sendMessage(queryToSend);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRegenerate = (lastUserMsg) => {
    if (lastUserMsg && !isLoading) {
      sendMessage(lastUserMsg);
    }
  };

  const promptStarters = [
    {
      title: "Attendance Regulations",
      desc: "What is the minimum attendance percentage required to sit for exams?",
      icon: "📋",
      category: "Academic Rules"
    },
    {
      title: "Hostel Curfew & Leaves",
      desc: "What is the hostel in-time curfew on weekdays and how to apply for night-out?",
      icon: "🏢",
      category: "Residential Code"
    },
    {
      title: "Merit & Need Scholarships",
      desc: "Who qualifies for the 50% tuition waiver Merit Scholarship?",
      icon: "🎓",
      category: "Financial Aid"
    },
    {
      title: "Exam & Grading Code",
      desc: "What are the passing criteria and fee deadline for exam re-evaluation?",
      icon: "📝",
      category: "Examination"
    }
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0d0f17] text-slate-100 font-sans">
      {/* ChatGPT Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />

      {/* Main ChatGPT Conversation Canvas */}
      <main className="flex-1 flex flex-col h-full relative overflow-hidden bg-[#0a0c14]">
        {/* Top Floating ChatGPT Header */}
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 bg-[#0d0f17]/80 backdrop-blur-md z-20">
          <div className="flex items-center space-x-3">
            {/* Model Selector Pill */}
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 cursor-pointer transition-colors group">
              <span className="font-bold text-sm text-white">CampusMind 4.0</span>
              <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                RAG Grounded
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-white transition-colors" />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              title="Toggle theme"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-indigo-400" />}
            </button>
          </div>
        </header>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
          {messages.length === 0 ? (
            /* ChatGPT Welcome Screen */
            <div className="max-w-3xl mx-auto my-auto flex flex-col items-center justify-center min-h-[70vh] text-center px-4">
              {/* Glowing Icon */}
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-aurora-cyan via-aurora-blue to-aurora-purple p-0.5 shadow-2xl shadow-cyan-500/20 mb-6 flex items-center justify-center">
                <div className="w-full h-full bg-[#0d0f17] rounded-[14px] flex items-center justify-center">
                  <Bot className="w-8 h-8 text-aurora-cyan" />
                </div>
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                What can I help you discover about your campus?
              </h1>
              <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-md">
                Ask about university rules, attendance guidelines, exams, fees, or hostel codes. All answers are verified against official documents.
              </p>

              {/* 2x2 ChatGPT Prompt Cards */}
              <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
                {promptStarters.map((starter, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(starter.desc)}
                    className="p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.07] border border-white/5 hover:border-cyan-500/30 text-left transition-all duration-200 group"
                  >
                    <div className="flex items-center space-x-2 text-xs font-semibold text-white group-hover:text-aurora-cyan transition-colors mb-1">
                      <span>{starter.icon}</span>
                      <span>{starter.title}</span>
                    </div>
                    <p className="text-[12px] text-slate-400 leading-relaxed group-hover:text-slate-300">
                      {starter.desc}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Conversation Bubble Stream */
            <div className="max-w-3xl mx-auto w-full space-y-6">
              {messages.map((msg, idx) => {
                const isUser = msg.role === 'user';
                return (
                  <div
                    key={msg.id || idx}
                    className={`flex items-start space-x-4 ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    {/* Assistant Avatar */}
                    {!isUser && (
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-aurora-cyan to-aurora-blue flex items-center justify-center shadow-md shadow-cyan-500/20 flex-shrink-0 mt-0.5">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}

                    {/* Content Box */}
                    <div className={`relative max-w-[88%] sm:max-w-[82%]`}>
                      {isUser ? (
                        /* User Message */
                        <div className="px-4 py-3 rounded-2xl bg-[#212638] text-white text-sm font-medium leading-relaxed shadow-sm">
                          {msg.content}
                        </div>
                      ) : (
                        /* Assistant ChatGPT Response */
                        <div className="space-y-3">
                          <div className="text-slate-200 text-sm leading-relaxed">
                            <StreamingMessage
                              content={msg.content}
                              isNew={streamingMessageId === msg.id}
                              onComplete={() => setStreamingMessageId(null)}
                            />
                          </div>

                          {/* Verifiable Source Citations */}
                          {msg.sources && msg.sources.length > 0 && (
                            <div className="pt-2">
                              <div className="flex flex-wrap gap-1.5">
                                {msg.sources.map((src, sIdx) => (
                                  <button
                                    key={sIdx}
                                    onClick={() => setActiveCitation(src)}
                                    className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-cyan-500/20 border border-white/10 hover:border-cyan-500/40 text-[11px] text-cyan-300 font-mono transition-all hover:scale-[1.02]"
                                    title="Click to inspect source excerpt and page"
                                  >
                                    <FileText className="w-3 h-3 text-cyan-400" />
                                    <span className="font-bold">{src.document_name}</span>
                                    <span className="text-slate-400">· P.{src.page_number}</span>
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* ChatGPT-style Action Bar */}
                          <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
                            <div className="flex items-center space-x-3 text-[11px] font-mono">
                              {msg.latency_ms > 0 && (
                                <span className="flex items-center space-x-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{msg.latency_ms} ms</span>
                                </span>
                              )}
                              {msg.confidence_score !== undefined && (
                                <span className="text-emerald-400 font-medium">
                                  Verified ({Math.round(msg.confidence_score * 100)}%)
                                </span>
                              )}
                            </div>

                            <div className="flex items-center space-x-1">
                              <button
                                onClick={() => handleCopy(msg.content, msg.id)}
                                className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
                                title="Copy response"
                              >
                                {copiedId === msg.id ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                              </button>

                              <button
                                onClick={() => setFeedbackTarget({ messageId: msg.id, rating: 'like' })}
                                className={`p-1.5 rounded-lg hover:bg-white/5 transition-colors ${
                                  msg.feedback === 'like' ? 'text-emerald-400' : 'text-slate-400 hover:text-emerald-400'
                                }`}
                                title="Helpful"
                              >
                                <ThumbsUp className="w-3.5 h-3.5" />
                              </button>

                              <button
                                onClick={() => setFeedbackTarget({ messageId: msg.id, rating: 'dislike' })}
                                className={`p-1.5 rounded-lg hover:bg-white/5 transition-colors ${
                                  msg.feedback === 'dislike' ? 'text-red-400' : 'text-slate-400 hover:text-red-400'
                                }`}
                                title="Report issue"
                              >
                                <ThumbsDown className="w-3.5 h-3.5" />
                              </button>

                              {idx > 0 && (
                                <button
                                  onClick={() => handleRegenerate(messages[idx - 1]?.content)}
                                  className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
                                  title="Regenerate answer"
                                >
                                  <RotateCcw className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* User Avatar */}
                    {isUser && (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center font-bold text-white text-xs flex-shrink-0 mt-0.5">
                        U
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Generating / Thinking Pulse */}
              {isLoading && (
                <div className="flex items-start space-x-4 justify-start">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-aurora-cyan to-aurora-blue flex items-center justify-center shadow-md animate-pulse">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 space-y-2">
                    <div className="flex items-center space-x-2 text-xs text-aurora-cyan font-mono">
                      <Sparkles className="w-3.5 h-3.5 animate-spin" />
                      <span>Thinking and verifying university documents...</span>
                    </div>
                    <div className="flex space-x-1.5 pt-1">
                      <div className="w-2 h-2 rounded-full bg-aurora-cyan animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 rounded-full bg-aurora-blue animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 rounded-full bg-aurora-purple animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-400">
                  {error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* ChatGPT Bottom Floating Input Box */}
        <div className="p-4 sm:p-6 bg-gradient-to-t from-[#0a0c14] via-[#0a0c14]/90 to-transparent">
          <div className="max-w-3xl mx-auto">
            <form
              onSubmit={handleSend}
              className="relative rounded-3xl bg-[#171a26] border border-white/10 focus-within:border-cyan-500/50 shadow-2xl transition-all duration-200"
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Ask CampusMind anything about university rules, exams, hostel..."
                disabled={isLoading}
                className="w-full py-3.5 pl-5 pr-14 bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none resize-none max-h-44 disabled:opacity-50 overflow-y-auto"
              />

              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-2.5 bottom-2.5 p-2 rounded-xl bg-gradient-to-r from-aurora-cyan to-aurora-blue text-white shadow-md shadow-cyan-500/20 hover:shadow-cyan-500/40 disabled:opacity-30 disabled:hover:shadow-none hover:scale-105 active:scale-95 transition-all duration-200"
                title="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            <p className="text-center text-[11px] text-slate-500 mt-2">
              CampusMind AI answers are strictly grounded in university documents. Please verify critical academic deadlines with your department.
            </p>
          </div>
        </div>
      </main>

      {/* Source Citation Inspector Modal */}
      {activeCitation && (
        <SourceInspectorModal
          citation={activeCitation}
          onClose={() => setActiveCitation(null)}
        />
      )}

      {/* Response Feedback Modal */}
      {feedbackTarget && (
        <FeedbackModal
          messageId={feedbackTarget.messageId}
          rating={feedbackTarget.rating}
          onSubmit={rateMessage}
          onClose={() => setFeedbackTarget(null)}
        />
      )}
    </div>
  );
};
