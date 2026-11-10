import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeCitation, setActiveCitation] = useState(null);
  const [suggestions, setSuggestions] = useState([]);

  // Fetch all chat sessions
  const loadSessions = useCallback(async () => {
    try {
      const data = await api.getChats();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  }, []);

  // Fetch suggestions
  const loadSuggestions = useCallback(async () => {
    try {
      const data = await api.getSuggestions();
      setSuggestions(data);
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    }
  }, []);

  useEffect(() => {
    loadSessions();
    loadSuggestions();
  }, [loadSessions, loadSuggestions]);

  // Load message history when activeSessionId changes
  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }

    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const history = await api.getChatHistory(activeSessionId);
        setMessages(history);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [activeSessionId]);

  // Start a new chat
  const startNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setError(null);
  };

  // Send a student question
  const sendMessage = async (queryText) => {
    if (!queryText.trim() || isLoading) return;

    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: queryText,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, tempUserMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.askQuestion(queryText, activeSessionId);

      // If this was a new chat, update active session
      if (!activeSessionId) {
        setActiveSessionId(response.session_id);
        loadSessions();
      }

      const assistantMsg = {
        id: response.message_id,
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        confidence_score: response.confidence_score,
        latency_ms: response.latency_ms,
        feedback: null,
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.message || 'Something went wrong while generating an answer.');
    } finally {
      setIsLoading(false);
    }
  };

  // Delete chat
  const deleteSession = async (sessionId) => {
    try {
      await api.deleteChat(sessionId);
      if (activeSessionId === sessionId) {
        startNewChat();
      }
      loadSessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  // Handle feedback rating
  const rateMessage = async (messageId, rating, comment = null) => {
    try {
      await api.submitFeedback(messageId, rating, comment);
      setMessages(prev =>
        prev.map(m => (m.id === messageId ? { ...m, feedback: rating } : m))
      );
    } catch (err) {
      console.error('Failed to rate message:', err);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        sessions,
        activeSessionId,
        setActiveSessionId,
        messages,
        isLoading,
        error,
        activeCitation,
        setActiveCitation,
        suggestions,
        startNewChat,
        sendMessage,
        deleteSession,
        rateMessage,
        loadSessions,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);
