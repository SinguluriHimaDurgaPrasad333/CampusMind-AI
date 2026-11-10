import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  GraduationCap,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Search,
  BookOpen,
  CheckCircle,
  FileText,
  Clock,
  Layers,
  Database,
  Award,
  Zap,
  HelpCircle
} from 'lucide-react';
import { useChat } from '../context/ChatContext';

export const LandingPage = () => {
  const navigate = useNavigate();
  const { sendMessage, startNewChat } = useChat();

  const samplePrompts = [
    {
      category: "Attendance",
      question: "What is the minimum attendance requirement to write semester exams?",
      icon: Clock,
      color: "from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/30"
    },
    {
      category: "Hostel Rules",
      question: "What is the hostel curfew time on weekdays and weekends?",
      icon: ShieldCheck,
      color: "from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/30"
    },
    {
      category: "Scholarships",
      question: "Who is eligible for the Merit Scholarship and what is the fee waiver?",
      icon: Award,
      color: "from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30"
    },
    {
      category: "Examinations",
      question: "What are the passing criteria and minimum marks in end-semester theory?",
      icon: FileText,
      color: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30"
    }
  ];

  const handlePromptClick = (question) => {
    startNewChat();
    navigate('/chat');
    // small timeout to allow ChatPage to mount
    setTimeout(() => {
      sendMessage(question);
    }, 150);
  };

  return (
    <div className="relative min-h-[calc(100vh-4rem)] overflow-hidden aurora-bg">
      {/* Background Floating Glow Elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-aurora-cyan/10 rounded-full blur-3xl pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-aurora-purple/15 rounded-full blur-3xl pointer-events-none animate-pulse-slow" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 relative z-10">
        
        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto">
          {/* Glowing Badge */}
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-slate-900/80 dark:bg-white/10 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 mb-6 backdrop-blur-md">
            <Sparkles className="w-4 h-4 text-aurora-cyan animate-pulse" />
            <span className="text-xs font-semibold tracking-wide text-slate-200 dark:text-slate-200">
              Retrieval-Augmented Generation (RAG) Architecture
            </span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight sm:leading-none">
            The AI Brain for Your <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-aurora-cyan via-aurora-blue to-aurora-purple bg-clip-text text-transparent">
              University Campus Journey
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-base sm:text-lg text-slate-300 dark:text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
            Get instant, accurate, and verifiable answers to questions about attendance regulations, syllabus, examination guidelines, hostel codes, fees, and academic calendars — grounded strictly in official institutional documents.
          </p>

          {/* CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/chat"
              className="w-full sm:w-auto flex items-center justify-center space-x-2.5 px-8 py-3.5 rounded-xl bg-gradient-to-r from-aurora-cyan via-aurora-blue to-aurora-purple text-white font-bold text-sm shadow-xl shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-105 transition-all duration-300"
            >
              <span>Start Chatting</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/knowledge-base"
              className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-3.5 rounded-xl glass-panel text-slate-200 hover:text-white hover:bg-slate-800/60 font-semibold text-sm transition-all duration-200 border border-slate-700/60"
            >
              <BookOpen className="w-4 h-4 text-aurora-cyan" />
              <span>Explore Knowledge Base</span>
            </Link>
          </div>

          {/* Trust Guarantees */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400">
            <div className="flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Zero Policy Hallucination</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-cyan-400" />
              <span>Verifiable Page Citations</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-purple-400" />
              <span>Sub-millisecond Vector Search</span>
            </div>
          </div>
        </div>

        {/* Live Performance Stats Banner */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
          {[
            { label: "Official Policy Docs", val: "8 Documents", sub: "Pre-indexed & Verified", icon: BookOpen },
            { label: "Semantic Retrieval Chunks", val: "52 Chunks", sub: "FAISS Vector Index", icon: Database },
            { label: "Benchmark Recall@K", val: "95.0%", sub: "MRR: 0.925", icon: Zap },
            { label: "Average Query Latency", val: "1.0 ms", sub: "Instant In-Memory Search", icon: Clock },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="glass-panel p-5 rounded-2xl border border-white/5 hover:border-cyan-500/30 transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-slate-400 font-medium">{stat.label}</span>
                  <Icon className="w-4 h-4 text-aurora-cyan opacity-80" />
                </div>
                <div className="text-2xl font-extrabold text-white font-mono">{stat.val}</div>
                <div className="text-[11px] text-slate-500 mt-0.5">{stat.sub}</div>
              </div>
            );
          })}
        </div>

        {/* Quick Demo Questions Section */}
        <div className="mt-20 max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-white">
              Try Common Student Inquiries
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Click any question below to test real-time retrieval with verifiable citations
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {samplePrompts.map((p, idx) => {
              const Icon = p.icon;
              return (
                <div
                  key={idx}
                  onClick={() => handlePromptClick(p.question)}
                  className={`group glass-panel p-5 rounded-2xl border cursor-pointer hover:scale-[1.02] transition-all duration-300 ${p.color}`}
                >
                  <div className="flex items-center space-x-3 mb-2.5">
                    <div className="p-2 rounded-xl bg-slate-900/60 border border-white/10">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-bold uppercase tracking-wider">
                      {p.category}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-white group-hover:text-aurora-cyan transition-colors">
                    "{p.question}"
                  </p>
                  <div className="mt-3 flex items-center justify-between text-[11px] opacity-75">
                    <span>Click to ask AI assistant</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* RAG Pipeline Architecture Highlights */}
        <div className="mt-24 max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-white">
              Production-Grade RAG Pipeline
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              How CampusMind AI guarantees trustworthy, grounded university answers
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <div className="w-10 h-10 rounded-xl bg-aurora-cyan/20 text-aurora-cyan flex items-center justify-center mb-4">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-white mb-2">1. Ingest & Chunk</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Extracts university documents (PDF, DOCX, TXT, CSV), normalizes content, and divides into overlapping semantic chunks preserving page boundaries and sections.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <div className="w-10 h-10 rounded-xl bg-aurora-blue/20 text-aurora-blue flex items-center justify-center mb-4">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-white mb-2">2. FAISS Vector Search</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Encodes questions into vector embeddings, performs inner product search in FAISS, and applies confidence thresholding to filter irrelevant passages.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <div className="w-10 h-10 rounded-xl bg-aurora-purple/20 text-aurora-purple flex items-center justify-center mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-white mb-2">3. Grounded Synthesis</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generates answers strictly from retrieved evidence with source citations. If information is missing, safely responds with institutional disclaimer.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
