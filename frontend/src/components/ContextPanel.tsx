import React from 'react';
import './ContextPanel.css';

interface ContextPanelProps {
  sources?: string[];
  notes?: string;
  onClose?: () => void;
}

export const ContextPanel: React.FC<ContextPanelProps> = ({
  sources = [],
  notes,
  onClose,
}) => {
  return (
    <div className="context-panel">
      <div className="context-header">
        <h3>Context</h3>
        {onClose && (
          <button
            className="context-close"
            onClick={onClose}
            aria-label="Close context panel"
          >
            ×
          </button>
        )}
      </div>
      <div className="context-content">
        {sources.length > 0 && (
          <div className="context-section">
            <h4>Sources</h4>
            <ul className="sources-list">
              {sources.map((source, index) => (
                <li key={index}>
                  <a href={source} target="_blank" rel="noopener noreferrer">
                    {source}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
        {notes && (
          <div className="context-section">
            <h4>Notes</h4>
            <div className="notes-content">{notes}</div>
          </div>
        )}
        {sources.length === 0 && !notes && (
          <div className="context-empty">
            <p>No context available</p>
          </div>
        )}
      </div>
    </div>
  );
};

