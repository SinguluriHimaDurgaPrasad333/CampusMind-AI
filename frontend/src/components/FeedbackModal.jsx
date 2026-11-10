import React, { useState } from 'react';
import { X, ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react';

export const FeedbackModal = ({ messageId, rating, onSubmit, onClose }) => {
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    await onSubmit(messageId, rating, comment);
    setIsSubmitting(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div 
        className="w-full max-w-md glass-panel rounded-2xl p-6 shadow-2xl border border-white/10"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-700/60">
          <div className="flex items-center space-x-2">
            {rating === 'like' ? (
              <ThumbsUp className="w-5 h-5 text-emerald-400" />
            ) : (
              <ThumbsDown className="w-5 h-5 text-red-400" />
            )}
            <h3 className="font-bold text-sm text-white">
              {rating === 'like' ? 'Helpful Response Feedback' : 'Report Issue with Response'}
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <p className="text-xs text-slate-300">
            {rating === 'like'
              ? 'Glad this was helpful! Let us know what made this answer accurate or useful.'
              : 'Help us improve CampusMind AI. What was missing or inaccurate about this answer?'}
          </p>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            placeholder="Additional comments (optional)..."
            className="w-full p-3 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-aurora-cyan resize-none"
          />

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 rounded-xl text-xs text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-aurora-cyan to-aurora-blue hover:opacity-90 shadow-md shadow-cyan-500/20"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
