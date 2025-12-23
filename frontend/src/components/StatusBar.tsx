import React from 'react';
import { Model } from '../types';
import './StatusBar.css';

interface StatusBarProps {
  connected: boolean;
  validated: boolean;
  provider?: string;
  model?: Model | null;
  tokenCount?: number;
  cost?: number;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  connected,
  validated,
  provider,
  model,
  tokenCount,
  cost,
}) => {
  return (
    <div className="status-bar">
      <div className="status-item">
        <span className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}></span>
        <span className="status-text">
          {connected && validated ? 'Connected / Validated' : 'Disconnected'}
        </span>
      </div>
      {provider && model && (
        <div className="status-item">
          <span className="status-label">Using:</span>
          <span className="status-value">
            {provider} {model.name}
          </span>
        </div>
      )}
      {tokenCount !== undefined && (
        <div className="status-item">
          <span className="status-label">Tokens:</span>
          <span className="status-value">{tokenCount.toLocaleString()}</span>
        </div>
      )}
      {cost !== undefined && cost > 0 && (
        <div className="status-item">
          <span className="status-label">Cost:</span>
          <span className="status-value">${cost.toFixed(4)}</span>
        </div>
      )}
    </div>
  );
};

