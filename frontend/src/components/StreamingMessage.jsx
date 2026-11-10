import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export const StreamingMessage = ({ content, isNew, onComplete }) => {
  const [displayedText, setDisplayedText] = useState(isNew ? '' : content);
  const [isStreaming, setIsStreaming] = useState(isNew);

  useEffect(() => {
    if (!isNew) {
      setDisplayedText(content);
      setIsStreaming(false);
      return;
    }

    let currentIndex = 0;
    const totalLength = content.length;
    // Dynamic speed: faster for longer texts so it completes in ~1.5 - 2.5 seconds
    const step = Math.max(2, Math.floor(totalLength / 80));
    const intervalTime = 16; // ~60fps

    const timer = setInterval(() => {
      currentIndex += step;
      if (currentIndex >= totalLength) {
        setDisplayedText(content);
        setIsStreaming(false);
        clearInterval(timer);
        if (onComplete) onComplete();
      } else {
        setDisplayedText(content.slice(0, currentIndex));
      }
    }, intervalTime);

    return () => clearInterval(timer);
  }, [content, isNew, onComplete]);

  return (
    <div className="prose-ai relative">
      <ReactMarkdown>{displayedText}</ReactMarkdown>
      {isStreaming && (
        <span className="inline-block w-2 h-4 ml-1 bg-aurora-cyan animate-pulse align-middle" />
      )}
    </div>
  );
};
