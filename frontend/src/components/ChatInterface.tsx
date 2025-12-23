import React, { useState, useRef, useEffect } from 'react';
import { Message, Model } from '../types';
import { chatAPI, sessionsAPI } from '../services/api';
import { ChatBubble } from './ChatBubble';
import './ChatInterface.css';

interface ChatInterfaceProps {
  messages: Message[];
  selectedModel: Model | null;
  apiKey: string;
  provider: string;
  sessionId: number | null;
  onMessageSent: (userMessage: string, assistantMessage: string, newSessionId?: number) => void;
  onTokenUpdate?: (tokens: number) => void;
  onStreamingChange?: (isStreaming: boolean) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  selectedModel,
  apiKey,
  provider,
  sessionId,
  onMessageSent,
  onTokenUpdate,
  onStreamingChange,
}) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<Array<{ name: string; content: string }>>([]);
  const [searchResults, setSearchResults] = useState<Array<{ title: string; snippet: string; url: string }>>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if ((!input.trim() && attachedFiles.length === 0) || !selectedModel || loading || isStreaming) return;

    const userMessage = input.trim();
    const messageWithFiles = buildMessageWithFiles(userMessage);
    setInput('');
    setAttachedFiles([]); // Clear attached files after sending
    setLoading(true);
    setIsStreaming(true);
    setStreamingMessage('');
    if (onStreamingChange) onStreamingChange(true);

    // Create session if it doesn't exist BEFORE sending
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      try {
        const newSession = await sessionsAPI.create();
        currentSessionId = newSession.id;
        // Update parent component's session state
        // We'll pass this to onMessageSent callback
      } catch (error) {
        console.error('Error creating session:', error);
        // Continue without session - message won't be saved
      }
    }

    try {
      let fullResponse = '';

      await chatAPI.sendMessageStream(
        {
          provider,
          api_key: apiKey,
          model: selectedModel.id,
          prompt: messageWithFiles,
          session_id: currentSessionId || undefined,
          temperature: 0.7,
          enable_search: true,
        },
        (chunk) => {
          fullResponse += chunk;
          setStreamingMessage(fullResponse);
          if (onTokenUpdate) {
            // Rough token estimate (4 chars per token)
            onTokenUpdate(Math.ceil(fullResponse.length / 4));
          }
        },
        (finalResponse) => {
          fullResponse = finalResponse;
          setStreamingMessage('');
          setIsStreaming(false);
          setLoading(false);
          setSearchResults([]); // Clear search results after message is done
          if (onStreamingChange) onStreamingChange(false);
          // Pass the session ID if we created a new one
          onMessageSent(messageWithFiles, finalResponse, currentSessionId || undefined);
        },
        (error) => {
          console.error('Streaming error:', error);
          setStreamingMessage('');
          setIsStreaming(false);
          setLoading(false);
          if (onStreamingChange) onStreamingChange(false);
          alert(`Error: ${error}`);
        },
        (searchData: any) => {
          // Handle search results
          if (searchData.type === 'search_results') {
            // Parse search results from the content
            try {
              const lines = searchData.content.split('\n');
              const results: Array<{ title: string; snippet: string; url: string }> = [];
              let currentResult: any = null;
              
              for (const line of lines) {
                if (line.match(/^\d+\./)) {
                  if (currentResult) results.push(currentResult);
                  currentResult = { title: line.replace(/^\d+\.\s*/, ''), snippet: '', url: '' };
                } else if (line.startsWith('   URL:')) {
                  if (currentResult) currentResult.url = line.replace('   URL:', '').trim();
                } else if (line.startsWith('   ') && currentResult) {
                  currentResult.snippet += line.trim() + ' ';
                }
              }
              if (currentResult) results.push(currentResult);
              
              setSearchResults(results);
            } catch (e) {
              console.error('Error parsing search results:', e);
            }
          }
        }
      );
    } catch (error: any) {
      console.error('Error sending message:', error);
      setStreamingMessage('');
      setIsStreaming(false);
      setLoading(false);
      if (onStreamingChange) onStreamingChange(false);
      alert(error.response?.data?.detail || 'Failed to send message');
    }
  };

  const handleRegenerate = async (lastUserMessage: string) => {
    if (!selectedModel || loading || isStreaming) return;
    setLoading(true);
    setIsStreaming(true);
    setStreamingMessage('');
    if (onStreamingChange) onStreamingChange(true);

    try {
      let fullResponse = '';

      await chatAPI.sendMessageStream(
        {
          provider,
          api_key: apiKey,
          model: selectedModel.id,
          prompt: lastUserMessage,
          session_id: sessionId || undefined,
          temperature: 0.7,
        },
        (chunk) => {
          fullResponse += chunk;
          setStreamingMessage(fullResponse);
        },
        (finalResponse) => {
          fullResponse = finalResponse;
          setStreamingMessage('');
          setIsStreaming(false);
          setLoading(false);
          if (onStreamingChange) onStreamingChange(false);
          onMessageSent(lastUserMessage, finalResponse);
        },
        (error) => {
          console.error('Streaming error:', error);
          setStreamingMessage('');
          setIsStreaming(false);
          setLoading(false);
          if (onStreamingChange) onStreamingChange(false);
          alert(`Error: ${error}`);
        }
      );
    } catch (error: any) {
      console.error('Error regenerating:', error);
      setStreamingMessage('');
      setIsStreaming(false);
      setLoading(false);
      if (onStreamingChange) onStreamingChange(false);
      alert(error.response?.data?.detail || 'Failed to regenerate');
    }
  };

  const getLastUserMessage = () => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        return messages[i].content;
      }
    }
    return '';
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const newFiles: Array<{ name: string; content: string }> = [];

    for (const file of Array.from(files)) {
      // Only accept text files for now
      if (file.type.startsWith('text/') || 
          file.type === 'application/json' ||
          file.name.endsWith('.txt') ||
          file.name.endsWith('.md') ||
          file.name.endsWith('.json') ||
          file.name.endsWith('.csv')) {
        try {
          const content = await file.text();
          newFiles.push({ name: file.name, content });
        } catch (error) {
          console.error(`Error reading file ${file.name}:`, error);
          alert(`Failed to read file: ${file.name}`);
        }
      } else {
        alert(`File type not supported: ${file.name}. Please upload text files only.`);
      }
    }

    if (newFiles.length > 0) {
      setAttachedFiles([...attachedFiles, ...newFiles]);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemoveFile = (index: number) => {
    setAttachedFiles(attachedFiles.filter((_, i) => i !== index));
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const buildMessageWithFiles = (userMessage: string): string => {
    if (attachedFiles.length === 0) {
      return userMessage;
    }

    let message = userMessage;
    if (attachedFiles.length > 0) {
      message += '\n\n--- Attached Files ---\n';
      attachedFiles.forEach((file) => {
        message += `\n[File: ${file.name}]\n${file.content}\n`;
      });
    }

    return message;
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && !isStreaming ? (
          <div className="empty-chat">
            <div className="welcome-content">
              <h2>Welcome to Research Assistant</h2>
              <p>Start a conversation or try these quick actions:</p>
              <div className="quick-actions">
                <button className="quick-action">📄 Import URLs</button>
                <button className="quick-action">📝 Summarize</button>
                <button className="quick-action">➕ New Session</button>
              </div>
            </div>
            {!selectedModel && (
              <p className="warning">Please select a model first.</p>
            )}
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatBubble
                key={message.id}
                message={message}
                onRegenerate={
                  message.role === 'assistant' && messages[messages.indexOf(message) - 1]?.role === 'user'
                    ? () => handleRegenerate(messages[messages.indexOf(message) - 1].content)
                    : undefined
                }
              />
            ))}
            {isStreaming && streamingMessage && (
              <div className="message assistant streaming">
                <div className="bubble-header">
                  <span className="bubble-role">Assistant</span>
                  {selectedModel && <span className="bubble-model">{selectedModel.name}</span>}
                  <span className="streaming-indicator">●</span>
                </div>
                <div className="bubble-content">{streamingMessage}</div>
              </div>
            )}
            {loading && !streamingMessage && (
              <div className="message assistant">
                <div className="bubble-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-container">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.md,.json,.csv,text/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          aria-label="File input"
        />
        {attachedFiles.length > 0 && (
          <div className="attached-files">
            {attachedFiles.map((file, index) => (
              <div key={index} className="attached-file">
                <span className="file-name">{file.name}</span>
                <button
                  className="file-remove"
                  onClick={() => handleRemoveFile(index)}
                  aria-label={`Remove ${file.name}`}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
        <div className="input-toolbar">
          <button
            className="toolbar-button"
            onClick={handleAttachClick}
            title="Upload file"
            aria-label="Upload file"
            disabled={loading || isStreaming}
          >
            📎
          </button>
          <button
            className="toolbar-button"
            onClick={() => setInput('')}
            disabled={!input}
            title="Clear input"
            aria-label="Clear input"
          >
            ✕
          </button>
          <button className="toolbar-button" title="Export" aria-label="Export">
            💾
          </button>
        </div>
        <textarea
          ref={textareaRef}
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder={
            selectedModel
              ? 'Type your message... (Press Enter to send, Shift+Enter for new line)'
              : 'Please select a model first...'
          }
          disabled={!selectedModel || loading || isStreaming}
          rows={1}
        />
        {attachedFiles.length > 0 && (
          <div className="file-count-badge">
            {attachedFiles.length} file{attachedFiles.length > 1 ? 's' : ''} attached
          </div>
        )}
        <button
          className="send-button"
          onClick={handleSend}
          disabled={!selectedModel || (!input.trim() && attachedFiles.length === 0) || loading || isStreaming}
          aria-label="Send message"
        >
          {loading || isStreaming ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
};
