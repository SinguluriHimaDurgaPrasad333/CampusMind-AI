import React from 'react';
import { X, FileText, CheckCircle2, Bookmark, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export const SourceInspectorModal = ({ citation, onClose }) => {
  if (!citation) return null;

  const scorePct = Math.min(100, Math.round(citation.score * 100));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div 
        className="relative w-full max-w-lg glass-panel rounded-2xl p-6 shadow-2xl border border-aurora-cyan/30 text-slate-100 dark:text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-700/60 dark:border-white/10">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-aurora-cyan/20 text-aurora-cyan border border-aurora-cyan/30">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white truncate max-w-[320px]">
                {citation.document_name}
              </h3>
              <div className="flex items-center space-x-2 mt-0.5">
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 dark:bg-white/10 text-aurora-cyan font-medium border border-cyan-500/20">
                  {citation.category}
                </span>
                <span className="text-[11px] text-slate-400">
                  Page {citation.page_number}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="mt-4 space-y-4">
          {/* Retrieval Confidence Indicator */}
          <div>
            <div className="flex items-center justify-between text-xs mb-1.5 font-medium">
              <span className="text-slate-300">Retrieval Relevance Score</span>
              <span className="text-aurora-cyan font-mono font-bold">
                {scorePct}% ({citation.score})
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-aurora-blue to-aurora-cyan rounded-full transition-all duration-500"
                style={{ width: `${Math.max(15, scorePct)}%` }}
              />
            </div>
          </div>

          {/* Verbatim Context Passage */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Retrieved Evidence Passage
            </label>
            <div className="p-4 rounded-xl bg-slate-900/90 dark:bg-black/50 border border-slate-800 text-xs font-mono text-slate-200 leading-relaxed max-h-60 overflow-y-auto whitespace-pre-wrap selection:bg-cyan-500/30">
              {citation.snippet}
            </div>
          </div>

          {/* Grounding notice */}
          <div className="flex items-center space-x-2 text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-2 rounded-lg">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>This verifiable institutional excerpt directly supports the AI assistant's answer.</span>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
          <Link
            to="/knowledge-base"
            onClick={onClose}
            className="flex items-center space-x-1.5 text-xs text-aurora-cyan hover:underline"
          >
            <span>Explore Knowledge Base</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
