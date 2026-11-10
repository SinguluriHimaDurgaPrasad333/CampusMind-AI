const API_BASE = '/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('campusmind_admin_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  // Chat Endpoints
  async askQuestion(query, sessionId = null) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to generate answer.');
    }
    return res.json();
  },

  async getChats() {
    const res = await fetch(`${API_BASE}/chats`);
    if (!res.ok) throw new Error('Failed to fetch conversations.');
    return res.json();
  },

  async getChatHistory(chatId) {
    const res = await fetch(`${API_BASE}/chats/${chatId}`);
    if (!res.ok) throw new Error('Failed to load chat history.');
    return res.json();
  },

  async deleteChat(chatId) {
    const res = await fetch(`${API_BASE}/chats/${chatId}`, {
      method: 'DELETE',
    });
    return res.json();
  },

  async submitFeedback(messageId, feedback, comment = null) {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id: messageId, feedback, comment }),
    });
    return res.json();
  },

  // Knowledge Base & Admin
  async getDocuments() {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents.');
    return res.json();
  },

  async adminLogin(username, password) {
    const res = await fetch(`${API_BASE}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid admin credentials');
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('campusmind_admin_token', data.access_token);
      localStorage.setItem('campusmind_admin_user', data.username);
    }
    return data;
  },

  async uploadDocument(formData) {
    const res = await fetch(`${API_BASE}/admin/documents/upload`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload document.');
    }
    return res.json();
  },

  async deleteDocument(documentId) {
    const res = await fetch(`${API_BASE}/admin/documents/${documentId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeaders() },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to delete document.');
    }
    return res.json();
  },

  async reindexDocuments() {
    const res = await fetch(`${API_BASE}/admin/reindex`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to rebuild index.');
    }
    return res.json();
  },

  // Analytics & Suggestions
  async getAnalytics() {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics.');
    return res.json();
  },

  async getSuggestions() {
    const res = await fetch(`${API_BASE}/suggestions`);
    if (!res.ok) return [];
    return res.json();
  },

  // Evaluation Benchmark
  async runEvaluation() {
    const res = await fetch(`${API_BASE}/evaluate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Evaluation benchmark run failed.');
    return res.json();
  },
};
