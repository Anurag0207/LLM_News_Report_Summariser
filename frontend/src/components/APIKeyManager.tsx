import React, { useState, useEffect } from 'react';
import { Provider } from '../types';
import { authAPI, modelsAPI } from '../services/api';
import { CollapsibleSection } from './CollapsibleSection';
import './APIKeyManager.css';

interface APIKeyManagerProps {
  onKeyValidated: (provider: Provider, apiKey: string, models: any[]) => void;
}

const providers: { value: Provider; label: string }[] = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'gemini', label: 'Google Gemini' },
  { value: 'openrouter', label: 'OpenRouter' },
];

// Helper functions for localStorage
const getStoredApiKey = (provider: Provider): string => {
  try {
    const stored = localStorage.getItem(`api_key_${provider}`);
    return stored || '';
  } catch {
    return '';
  }
};

const setStoredApiKey = (provider: Provider, apiKey: string): void => {
  try {
    localStorage.setItem(`api_key_${provider}`, apiKey);
  } catch (error) {
    console.error('Failed to store API key:', error);
  }
};

const getStoredProvider = (): Provider => {
  try {
    const stored = localStorage.getItem('api_provider');
    return (stored as Provider) || 'openai';
  } catch {
    return 'openai';
  }
};

const setStoredProvider = (provider: Provider): void => {
  try {
    localStorage.setItem('api_provider', provider);
  } catch (error) {
    console.error('Failed to store provider:', error);
  }
};

export const APIKeyManager: React.FC<APIKeyManagerProps> = ({ onKeyValidated }) => {
  const [provider, setProvider] = useState<Provider>(getStoredProvider());
  const [apiKey, setApiKey] = useState(() => getStoredApiKey(getStoredProvider()));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isValidated, setIsValidated] = useState(false);

  // Load API key when provider changes
  useEffect(() => {
    const storedKey = getStoredApiKey(provider);
    setApiKey(storedKey);
    setIsValidated(!!storedKey);
  }, [provider]);

  // Auto-validate on mount if API key exists (only once)
  useEffect(() => {
    const currentProvider = getStoredProvider();
    const storedKey = getStoredApiKey(currentProvider);
    if (storedKey && storedKey.length > 0) {
      // Auto-validate in the background
      const autoValidate = async () => {
        try {
          setLoading(true);
          const validation = await authAPI.validateKey({
            provider: currentProvider,
            api_key: storedKey,
          });
          
          if (validation.valid) {
            const models = await modelsAPI.listModels({
              provider: currentProvider,
              api_key: storedKey,
            });
            setIsValidated(true);
            onKeyValidated(currentProvider, storedKey, models);
          } else {
            setIsValidated(false);
          }
        } catch (err) {
          setIsValidated(false);
        } finally {
          setLoading(false);
        }
      };
      autoValidate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const handleValidate = async () => {
    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Validate key
      const validation = await authAPI.validateKey({
        provider,
        api_key: apiKey,
      });

      if (!validation.valid) {
        setError(validation.message);
        setLoading(false);
        setIsValidated(false);
        return;
      }

      // Fetch models
      const models = await modelsAPI.listModels({
        provider,
        api_key: apiKey,
      });

      // Store API key and provider in localStorage
      setStoredApiKey(provider, apiKey);
      setStoredProvider(provider);
      setIsValidated(true);

      onKeyValidated(provider, apiKey, models);
      // Don't clear the API key - keep it in the input field
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to validate API key');
      setIsValidated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = (newProvider: Provider) => {
    setProvider(newProvider);
    setStoredProvider(newProvider);
    setError(null);
    setIsValidated(false);
  };

  return (
    <CollapsibleSection title="API Key Configuration" defaultOpen={true}>
      <div className="api-key-manager">
        <div className="api-key-form">
          <div className="form-group">
            <label htmlFor="provider">Provider:</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => handleProviderChange(e.target.value as Provider)}
              disabled={loading}
              aria-label="Select provider"
            >
              {providers.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="apiKey">API Key:</label>
            <div className="api-key-input-wrapper">
              <input
                id="apiKey"
                type="password"
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setIsValidated(false);
                }}
                placeholder={isValidated ? "API key saved (click to edit)" : "Enter your API key"}
                disabled={loading}
                onKeyPress={(e) => e.key === 'Enter' && handleValidate()}
                aria-label="Enter API key"
                className={isValidated ? 'api-key-validated' : ''}
              />
              {isValidated && (
                <span className="api-key-status" title="API key is validated and saved">
                  ✓
                </span>
              )}
            </div>
          </div>
          {error && <div className="error-message" role="alert">{error}</div>}
          {isValidated && !error && (
            <div className="success-message" role="alert">
              API key validated and saved
            </div>
          )}
          <button
            onClick={handleValidate}
            disabled={loading || !apiKey.trim()}
            className="validate-button"
            aria-label="Validate API key"
          >
            {loading ? 'Validating...' : isValidated ? 'Re-validate API Key' : 'Validate & Load Models'}
          </button>
        </div>
      </div>
    </CollapsibleSection>
  );
};

