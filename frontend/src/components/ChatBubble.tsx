import React, { useState } from 'react';
import { Message } from '../types';
import './ChatBubble.css';

interface ChatBubbleProps {
  message: Message;
  onRegenerate?: () => void;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message, onRegenerate }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`chat-bubble ${message.role}`}>
      <div className="bubble-header">
        <span className="bubble-role">
          {message.role === 'user' ? 'You' : 'Assistant'}
        </span>
        {message.model_used && (
          <span className="bubble-model">{message.model_used}</span>
        )}
        <span className="bubble-time">{formatTime(message.created_at)}</span>
      </div>
      <div className="bubble-content">{message.content}</div>
      <div className="bubble-actions">
        <button
          className="bubble-action"
          onClick={handleCopy}
          title="Copy message"
          aria-label="Copy message"
        >
          {copied ? '✓' : '📋'}
        </button>
        {message.role === 'assistant' && onRegenerate && (
          <button
            className="bubble-action"
            onClick={onRegenerate}
            title="Regenerate response"
            aria-label="Regenerate response"
          >
            🔄
          </button>
        )}
      </div>
    </div>
  );
};

