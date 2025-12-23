import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import './TopNav.css';

interface TopNavProps {
  onSettingsClick?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ onSettingsClick }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="top-nav">
      <div className="nav-left">
        <h1 className="nav-title">Research Assistant</h1>
        <span className="nav-subtitle">Multi-LLM Research Platform</span>
      </div>
      <div className="nav-right">
        <button
          className="nav-button"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          aria-label="Toggle theme"
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        {onSettingsClick && (
          <button
            className="nav-button"
            onClick={onSettingsClick}
            title="Settings"
            aria-label="Open settings"
          >
            ⚙️
          </button>
        )}
      </div>
    </nav>
  );
};

