import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  Filter,
  FileText,
  Calendar,
  Layers,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  X
} from 'lucide-react';
import { api } from '../services/api';

export const KnowledgeBasePage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['All', ...new Set(documents.map(d => d.category))];

  const filteredDocs = documents.filter(doc => {
    const matchesCat = selectedCategory === 'All' || doc.category === selectedCategory;
    const matchesSearch =
      doc.original_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8 aurora-bg">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800/80 dark:border-white/10">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-aurora-cyan/20 text-aurora-cyan border border-aurora-cyan/30">
                <BookOpen className="w-6 h-6" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
                University Knowledge Base
              </h1>
            </div>
            <p className="mt-1 text-xs sm:text-sm text-slate-400">
              Browse official institutional regulations, syllabi, calendars, and policies indexed for RAG retrieval.
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs font-mono px-3 py-1.5 rounded-xl glass-panel border border-cyan-500/30">
            <span className="text-slate-400">Total Indexed Documents:</span>
            <span className="font-bold text-aurora-cyan">{documents.length}</span>
          </div>
        </div>

        {/* Search & Category Filter Controls */}
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Search Bar */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search documents or policies..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl glass-panel border border-slate-700/80 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-aurora-cyan"
            />
          </div>

          {/* Category Chips Scroll */}
          <div className="flex items-center gap-2 overflow-x-auto w-full pb-1">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-gradient-to-r from-aurora-cyan to-aurora-blue text-white shadow-md shadow-cyan-500/20 font-semibold'
                    : 'glass-panel text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Documents Grid */}
        {loading ? (
          <div className="text-center py-20 text-slate-400 text-sm">
            <div className="w-8 h-8 rounded-full border-2 border-aurora-cyan border-t-transparent animate-spin mx-auto mb-3" />
            <p>Loading knowledge base corpus...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center py-20 glass-panel rounded-2xl border border-white/5">
            <FileText className="w-12 h-12 text-slate-500 mx-auto mb-3 opacity-40" />
            <p className="text-slate-300 font-semibold">No documents found</p>
            <p className="text-xs text-slate-500 mt-1">Try a different search term or category filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredDocs.map((doc) => (
              <div
                key={doc.id}
                onClick={() => setSelectedDoc(doc)}
                className="group glass-panel rounded-2xl p-5 border border-slate-800 hover:border-aurora-cyan/40 cursor-pointer hover:scale-[1.01] transition-all duration-300 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-aurora-cyan/15 text-aurora-cyan border border-aurora-cyan/25">
                      {doc.category}
                    </span>
                    <span className="flex items-center space-x-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Active</span>
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-white group-hover:text-aurora-cyan transition-colors line-clamp-2">
                    {doc.original_name}
                  </h3>
                </div>

                <div className="mt-5 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between font-mono">
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center space-x-1">
                      <Layers className="w-3.5 h-3.5 text-aurora-cyan" />
                      <span>{doc.chunk_count} Chunks</span>
                    </span>
                    <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-white group-hover:translate-x-0.5 transition-all" />
                </div>
              </div>
            ))}
          </div>
        )}

      </div>

      {/* Document Details Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div 
            className="w-full max-w-xl glass-panel rounded-2xl p-6 border border-cyan-500/30 text-white space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between pb-3 border-b border-slate-700">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 rounded-xl bg-aurora-cyan/20 text-aurora-cyan">
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-base">{selectedDoc.original_name}</h3>
                  <p className="text-xs text-aurora-cyan font-medium">{selectedDoc.category}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400 block mb-1">Vector Index Status:</span>
                <span className="text-emerald-400 font-bold">100% Retrievable (FAISS)</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400 block mb-1">Semantic Chunks:</span>
                <span className="text-white font-bold">{selectedDoc.chunk_count} Chunks</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400 block mb-1">File Format / Size:</span>
                <span className="text-white uppercase font-bold">{selectedDoc.file_type} ({(selectedDoc.file_size / 1024).toFixed(1)} KB)</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400 block mb-1">Policy Version:</span>
                <span className="text-white font-bold">v{selectedDoc.version}</span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              This document has been fully parsed, normalized, and embedded into the CampusMind FAISS index. Student queries referencing its topics will automatically retrieve its passages with verifiable citations.
            </p>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
