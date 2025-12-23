import React, { useState, useMemo } from 'react';
import { Model } from '../types';
import { CollapsibleSection } from './CollapsibleSection';
import './ModelSelector.css';

interface ModelSelectorProps {
  models: Model[];
  selectedModel: Model | null;
  onSelectModel: (model: Model) => void;
  currentProvider: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModel,
  onSelectModel,
  currentProvider,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredModels = useMemo(() => {
    if (!searchQuery.trim()) return models;
    const query = searchQuery.toLowerCase();
    return models.filter(
      (model) =>
        model.name.toLowerCase().includes(query) ||
        model.id.toLowerCase().includes(query)
    );
  }, [models, searchQuery]);

  if (models.length === 0) {
    return (
      <CollapsibleSection title="Model Selection" defaultOpen={true}>
        <p className="no-models">No models available. Please configure an API key.</p>
      </CollapsibleSection>
    );
  }

  return (
    <CollapsibleSection title="Model Selection" defaultOpen={true}>
      <div className="model-selector">
        <div className="model-search">
          <input
            type="text"
            placeholder="Search models..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
            aria-label="Search models"
          />
        </div>
        <div className="models-list">
          {filteredModels.length === 0 ? (
            <p className="no-results">No models found matching "{searchQuery}"</p>
          ) : (
            filteredModels.map((model) => (
              <div
                key={model.id}
                className={`model-card ${selectedModel?.id === model.id ? 'selected' : ''}`}
                onClick={() => onSelectModel(model)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectModel(model);
                  }
                }}
                tabIndex={0}
                role="button"
                aria-label={`Select model ${model.name}`}
              >
                <div className="model-header">
                  <div className="model-name">{model.name}</div>
                  {selectedModel?.id === model.id && (
                    <span className="selected-badge">✓</span>
                  )}
                </div>
                <div className="model-provider">{model.provider}</div>
                {/* Removed: model.description rendering to hide descriptions from UI */}
                <div className="model-capabilities">
                  <span className="capability-badge">Chat</span>
                  <span className="capability-badge">Text</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </CollapsibleSection>
  );
};
