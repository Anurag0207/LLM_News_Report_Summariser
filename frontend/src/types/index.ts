export interface Model {
  id: string;
  name: string;
  provider: string;
}

export interface Session {
  id: number;
  name: string;
  created_at: string;
  message_count: number;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  model_used: string | null;
  created_at: string;
}

export interface APIKeyConfig {
  provider: string;
  apiKey: string;
}

export type Provider = 'openai' | 'gemini' | 'openrouter';
