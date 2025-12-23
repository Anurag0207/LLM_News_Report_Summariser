import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { APIKeyManager } from './components/APIKeyManager';
import { ModelSelector } from './components/ModelSelector';
import { SessionTabs } from './components/SessionTabs';
import { ChatInterface } from './components/ChatInterface';
import { TopNav } from './components/TopNav';
import { StatusBar } from './components/StatusBar';
import { ResizablePanel } from './components/ResizablePanel';
import { ContextPanel } from './components/ContextPanel';
import { Model, Session, Message, Provider } from './types';
import { sessionsAPI } from './services/api';
import './App.css';

function App() {
  // Load API key and provider from localStorage on mount
  const [apiKey, setApiKey] = useState<string>(() => {
    try {
      const provider = (localStorage.getItem('api_provider') as Provider) || 'openai';
      return localStorage.getItem(`api_key_${provider}`) || '';
    } catch {
      return '';
    }
  });
  const [provider, setProvider] = useState<Provider>(() => {
    try {
      return (localStorage.getItem('api_provider') as Provider) || 'openai';
    } catch {
      return 'openai';
    }
  });
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [tokenCount, setTokenCount] = useState<number>(0);
  const [showContextPanel, setShowContextPanel] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Load messages when session changes (but delay to avoid interrupting streaming)
  useEffect(() => {
    if (activeSessionId && !isStreaming) {
      // Add a small delay to avoid interrupting any ongoing operations
      const timer = setTimeout(() => {
        loadMessages(activeSessionId);
      }, 300);
      return () => clearTimeout(timer);
    } else if (!activeSessionId) {
      setMessages([]);
    }
  }, [activeSessionId, isStreaming]);

  const loadSessions = async () => {
    try {
      const data = await sessionsAPI.list();
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        setActiveSessionId(data[0].id);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadMessages = async (sessionId: number) => {
    try {
      const data = await sessionsAPI.getMessages(sessionId);
      setMessages(data);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const handleKeyValidated = (newProvider: Provider, newApiKey: string, newModels: Model[]) => {
    setProvider(newProvider);
    setApiKey(newApiKey);
    setModels(newModels);
    if (newModels.length > 0) {
      setSelectedModel(newModels[0]);
    }
    // API key is already stored in localStorage by APIKeyManager
  };

  const handleCreateSession = async () => {
    try {
      const session = await sessionsAPI.create();
      setSessions([session, ...sessions]);
      setActiveSessionId(session.id);
      setMessages([]);
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session');
    }
  };

  const handleSelectSession = (sessionId: number) => {
    setActiveSessionId(sessionId);
  };

  const handleDeleteSession = async (sessionId: number) => {
    if (!confirm('Are you sure you want to delete this session?')) return;

    try {
      await sessionsAPI.delete(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        if (sessions.length > 1) {
          const remaining = sessions.filter((s) => s.id !== sessionId);
          setActiveSessionId(remaining[0]?.id || null);
        } else {
          setActiveSessionId(null);
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error);
      alert('Failed to delete session');
    }
  };

  const handleRenameSession = async (sessionId: number, newName: string) => {
    try {
      await sessionsAPI.rename(sessionId, newName);
      await loadSessions();
    } catch (error) {
      console.error('Error renaming session:', error);
      alert('Failed to rename session');
    }
  };

  const handleDuplicateSession = async (sessionId: number) => {
    try {
      const newSession = await sessionsAPI.duplicate(sessionId);
      setSessions([newSession, ...sessions]);
      setActiveSessionId(newSession.id);
      await loadMessages(newSession.id);
    } catch (error) {
      console.error('Error duplicating session:', error);
      alert('Failed to duplicate session');
    }
  };

  const handleMessageSent = async (userMessage: string, assistantMessage: string, newSessionId?: number) => {
    // Mark streaming as complete
    setIsStreaming(false);
    
    // If a new session was created, update the state
    if (newSessionId && newSessionId !== activeSessionId) {
      // Reload sessions to get the new one
      await loadSessions();
      setActiveSessionId(newSessionId);
      // Messages will be loaded when activeSessionId changes via useEffect (with delay)
      return;
    }
    
    // Messages are automatically saved by the backend when session_id is provided
    // Only reload messages after a delay to avoid interrupting the UI update
    if (activeSessionId) {
      // Use setTimeout to avoid interrupting the streaming UI
      setTimeout(async () => {
        await loadMessages(activeSessionId!);
      }, 1500); // Delay to let streaming UI update complete
    }
  };

  const handleTokenUpdate = (tokens: number) => {
    setTokenCount(tokens);
  };

  const isConnected = apiKey.length > 0 && selectedModel !== null;
  const isValidated = models.length > 0;

  return (
    <ThemeProvider>
      <div className="app">
        <TopNav />
        <div className="app-content">
          <ResizablePanel
            left={
              <div className="sidebar">
                <APIKeyManager onKeyValidated={handleKeyValidated} />
                {models.length > 0 && (
                  <ModelSelector
                    models={models}
                    selectedModel={selectedModel}
                    onSelectModel={setSelectedModel}
                    currentProvider={provider}
                  />
                )}
              </div>
            }
            right={
              <div className="main-content">
                <SessionTabs
                  sessions={sessions}
                  activeSessionId={activeSessionId}
                  onSelectSession={handleSelectSession}
                  onDeleteSession={handleDeleteSession}
                  onRenameSession={handleRenameSession}
                  onDuplicateSession={handleDuplicateSession}
                  onCreateSession={handleCreateSession}
                />
                <div className="chat-container">
                  {showContextPanel ? (
                    <ResizablePanel
                      left={
                        <ChatInterface
                          messages={messages}
                          selectedModel={selectedModel}
                          apiKey={apiKey}
                          provider={provider}
                          sessionId={activeSessionId}
                          onMessageSent={handleMessageSent}
                          onTokenUpdate={handleTokenUpdate}
                          onStreamingChange={setIsStreaming}
                        />
                      }
                      right={
                        <ContextPanel
                          sources={[]}
                          notes=""
                          onClose={() => setShowContextPanel(false)}
                        />
                      }
                      defaultLeftWidth={1}
                      minRightWidth={200}
                    />
                  ) : (
                    <ChatInterface
                      messages={messages}
                      selectedModel={selectedModel}
                      apiKey={apiKey}
                      provider={provider}
                      sessionId={activeSessionId}
                      onMessageSent={handleMessageSent}
                      onTokenUpdate={handleTokenUpdate}
                      onStreamingChange={setIsStreaming}
                    />
                  )}
                  <StatusBar
                    connected={isConnected}
                    validated={isValidated}
                    provider={provider}
                    model={selectedModel}
                    tokenCount={tokenCount}
                  />
                </div>
              </div>
            }
            defaultLeftWidth={350}
            minLeftWidth={250}
            minRightWidth={400}
          />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
