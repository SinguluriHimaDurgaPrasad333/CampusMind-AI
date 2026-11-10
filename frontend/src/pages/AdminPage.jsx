import React, { useState, useEffect } from 'react';
import {
  Shield,
  Upload,
  Trash2,
  RefreshCw,
  FileText,
  CheckCircle,
  AlertCircle,
  Lock,
  Layers,
  Database,
  Info,
  LogOut
} from 'lucide-react';
import { api } from '../services/api';

export const AdminPage = () => {
  const [token, setToken] = useState(() => localStorage.getItem('campusmind_admin_token'));
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  // Upload Form State
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadCategory, setUploadCategory] = useState('Attendance Policies');
  const [uploadVersion, setUploadVersion] = useState('2025.1');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [uploadError, setUploadError] = useState('');

  // Reindex state
  const [reindexing, setReindexing] = useState(false);
  const [reindexMsg, setReindexMsg] = useState('');

  useEffect(() => {
    if (token) {
      loadDocs();
    }
  }, [token]);

  const loadDocs = async () => {
    try {
      setLoadingDocs(true);
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      const data = await api.adminLogin(username, password);
      setToken(data.access_token);
    } catch (err) {
      setLoginError(err.message || 'Login failed. Please check credentials.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('campusmind_admin_token');
    localStorage.removeItem('campusmind_admin_user');
    setToken(null);
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError('Please select a file to upload.');
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadSuccess('');

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('category', uploadCategory);
    formData.append('version', uploadVersion);

    try {
      const res = await api.uploadDocument(formData);
      setUploadSuccess(`Successfully uploaded and indexed "${uploadFile.name}" into ${res.chunks_created} semantic chunks!`);
      setUploadFile(null);
      // Reset input element
      const fileInput = document.getElementById('admin-file-input');
      if (fileInput) fileInput.value = '';
      loadDocs();
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId, docName) => {
    if (!window.confirm(`Are you sure you want to delete "${docName}"? Its chunks will be permanently removed from the FAISS vector index.`)) {
      return;
    }
    try {
      await api.deleteDocument(docId);
      loadDocs();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleReindex = async () => {
    if (!window.confirm('Rebuild entire vector index from all active documents?')) return;
    setReindexing(true);
    setReindexMsg('');
    try {
      const res = await api.reindexDocuments();
      setReindexMsg(res.message);
      loadDocs();
    } catch (err) {
      alert(`Reindexing failed: ${err.message}`);
    } finally {
      setReindexing(false);
    }
  };

  // If not logged in, show Admin Login View
  if (!token) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 aurora-bg">
        <div className="w-full max-w-md glass-panel rounded-3xl p-8 border border-white/10 shadow-2xl space-y-6">
          <div className="text-center">
            <div className="inline-flex p-3 rounded-2xl bg-aurora-cyan/20 text-aurora-cyan border border-aurora-cyan/30 shadow-lg shadow-cyan-500/20 mb-3">
              <Shield className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-white">Administrator Access</h2>
            <p className="text-xs text-slate-400 mt-1">
              Authenticate to manage university documents and vector indexes
            </p>
          </div>

          {/* Quick Demo Credentials Tip */}
          <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-xs text-cyan-300 flex items-start space-x-2.5">
            <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Default Demo Credentials:</span>
              <p className="font-mono text-[11px] mt-0.5">Username: <strong>admin</strong> | Password: <strong>campusmind2025</strong></p>
            </div>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Admin Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-4 py-2.5 rounded-xl glass-panel border border-slate-700 text-sm text-white focus:outline-none focus:border-aurora-cyan"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter admin password..."
                className="w-full px-4 py-2.5 rounded-xl glass-panel border border-slate-700 text-sm text-white focus:outline-none focus:border-aurora-cyan"
              />
            </div>

            {loginError && (
              <p className="text-xs text-red-400 bg-red-500/10 p-2.5 rounded-lg border border-red-500/20">
                {loginError}
              </p>
            )}

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-aurora-cyan to-aurora-blue text-white font-bold text-sm shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-200"
            >
              Sign In to Admin Portal
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Admin Dashboard View
  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8 aurora-bg">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-aurora-cyan/20 text-aurora-cyan">
                <Shield className="w-6 h-6" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
                Admin Document Management
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Upload, validate, chunk, embed, and manage the university institutional corpus.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="flex items-center space-x-2 px-4 py-2 rounded-xl glass-panel text-xs font-semibold text-aurora-cyan hover:bg-slate-800 border border-cyan-500/30 transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reindexing ? 'animate-spin' : ''}`} />
              <span>{reindexing ? 'Rebuilding...' : 'Rebuild FAISS Index'}</span>
            </button>

            <button
              onClick={handleLogout}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 text-xs font-semibold border border-red-500/20 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {reindexMsg && (
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
            <span>{reindexMsg}</span>
          </div>
        )}

        {/* Upload Form Card */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 shadow-xl space-y-6">
          <div className="flex items-center space-x-2">
            <Upload className="w-5 h-5 text-aurora-cyan" />
            <h2 className="text-lg font-bold text-white">Upload New University Document</h2>
          </div>

          <form onSubmit={handleFileUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* File input */}
              <div className="md:col-span-1">
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Select Document (PDF, DOCX, TXT, CSV)
                </label>
                <input
                  id="admin-file-input"
                  type="file"
                  accept=".pdf,.docx,.doc,.txt,.csv,.md"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full text-xs text-slate-300 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-aurora-cyan/20 file:text-aurora-cyan hover:file:bg-aurora-cyan/30 cursor-pointer"
                />
              </div>

              {/* Category */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Knowledge Category
                </label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-panel border border-slate-700 text-xs text-white focus:outline-none focus:border-aurora-cyan"
                >
                  <option value="Attendance Policies" className="bg-space-900">Attendance Policies</option>
                  <option value="Academic Calendars" className="bg-space-900">Academic Calendars</option>
                  <option value="Examination Guidelines" className="bg-space-900">Examination Guidelines</option>
                  <option value="Hostel Rules and Regulations" className="bg-space-900">Hostel Rules and Regulations</option>
                  <option value="Scholarship Information" className="bg-space-900">Scholarship Information</option>
                  <option value="Fee-related Policies" className="bg-space-900">Fee-related Policies</option>
                  <option value="University Syllabus and Course Details" className="bg-space-900">University Syllabus & Courses</option>
                  <option value="Frequently Asked Questions (FAQs) & Administrative Policies" className="bg-space-900">Administrative FAQs</option>
                </select>
              </div>

              {/* Version */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Policy Version
                </label>
                <input
                  type="text"
                  value={uploadVersion}
                  onChange={(e) => setUploadVersion(e.target.value)}
                  placeholder="e.g. 2025-2026"
                  className="w-full px-3 py-2 rounded-xl glass-panel border border-slate-700 text-xs text-white focus:outline-none focus:border-aurora-cyan"
                />
              </div>
            </div>

            {uploadSuccess && (
              <p className="text-xs text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/30">
                {uploadSuccess}
              </p>
            )}

            {uploadError && (
              <p className="text-xs text-red-400 bg-red-500/10 p-3 rounded-xl border border-red-500/30">
                {uploadError}
              </p>
            )}

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={uploading || !uploadFile}
                className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-aurora-cyan to-aurora-blue text-white font-bold text-xs shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/35 disabled:opacity-40 transition-all"
              >
                <Upload className="w-4 h-4" />
                <span>{uploading ? 'Processing & Indexing...' : 'Upload & Embed Into Vector Store'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Existing Documents Table */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-aurora-cyan" />
              <h2 className="text-lg font-bold text-white">Active Knowledge Base Documents</h2>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {documents.length} Total Documents
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-3">Document Name</th>
                  <th className="py-3 px-3">Category</th>
                  <th className="py-3 px-3">Chunks</th>
                  <th className="py-3 px-3">Size</th>
                  <th className="py-3 px-3">Version</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {loadingDocs ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">
                      Loading documents...
                    </td>
                  </tr>
                ) : documents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">
                      No documents available. Upload one above!
                    </td>
                  </tr>
                ) : (
                  documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-3 font-medium text-white max-w-xs truncate">
                        {doc.original_name}
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded-full bg-slate-800 text-aurora-cyan text-[10px] border border-cyan-500/20">
                          {doc.category}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-300">
                        {doc.chunk_count}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-400">
                        {(doc.file_size / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-400">
                        v{doc.version}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => handleDelete(doc.id, doc.original_name)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title="Delete document and remove from FAISS"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};
