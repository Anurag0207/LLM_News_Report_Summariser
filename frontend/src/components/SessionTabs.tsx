import React, { useState } from 'react';
import { Session } from '../types';
import './SessionTabs.css';

interface SessionTabsProps {
  sessions: Session[];
  activeSessionId: number | null;
  onSelectSession: (sessionId: number) => void;
  onDeleteSession: (sessionId: number) => void;
  onRenameSession: (sessionId: number, newName: string) => void;
  onDuplicateSession: (sessionId: number) => void;
  onCreateSession: () => void;
}

export const SessionTabs: React.FC<SessionTabsProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onRenameSession,
  onDuplicateSession,
  onCreateSession,
}) => {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');

  const handleRenameStart = (session: Session, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditName(session.name);
  };

  const handleRenameSubmit = (sessionId: number) => {
    if (editName.trim()) {
      onRenameSession(sessionId, editName.trim());
    }
    setEditingId(null);
    setEditName('');
  };

  const handleRenameCancel = () => {
    setEditingId(null);
    setEditName('');
  };

  return (
    <div className="session-tabs">
      <div className="tabs-container">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`tab ${activeSessionId === session.id ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            {editingId === session.id ? (
              <input
                className="tab-rename-input"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onBlur={() => handleRenameSubmit(session.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleRenameSubmit(session.id);
                  } else if (e.key === 'Escape') {
                    handleRenameCancel();
                  }
                  e.stopPropagation();
                }}
                onClick={(e) => e.stopPropagation()}
                autoFocus
              />
            ) : (
              <>
                <span className="tab-name">{session.name}</span>
                <div className="tab-actions">
                  <button
                    className="tab-action"
                    onClick={(e) => handleRenameStart(session, e)}
                    title="Rename session"
                    aria-label="Rename session"
                  >
                    ✏️
                  </button>
                  <button
                    className="tab-action"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDuplicateSession(session.id);
                    }}
                    title="Duplicate session"
                    aria-label="Duplicate session"
                  >
                    📋
                  </button>
                  <button
                    className="tab-action tab-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    title="Delete session"
                    aria-label="Delete session"
                  >
                    ×
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
        <button
          className="new-tab-button"
          onClick={onCreateSession}
          title="New session"
          aria-label="Create new session"
        >
          +
        </button>
      </div>
    </div>
  );
};

