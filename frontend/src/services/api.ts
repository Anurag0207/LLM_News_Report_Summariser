import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ValidateKeyRequest {
  provider: string;
  api_key: string;
}

export interface ValidateKeyResponse {
  valid: boolean;
  message: string;
}

export interface ListModelsRequest {
  provider: string;
  api_key: string;
}

export interface ChatRequest {
  provider: string;
  api_key: string;
  model: string;
  prompt: string;
  session_id?: number;
  temperature?: number;
  max_tokens?: number;
  enable_search?: boolean;
  search_api_key?: string;
}

export interface ChatResponse {
  response: string;
  model_used: string;
  session_id?: number;
}

export interface ProcessURLsRequest {
  urls: string[];
}

export interface ProcessedURL {
  title: string;
  content: string;
  url: string;
  success: boolean;
  error?: string;
}

export const authAPI = {
  validateKey: async (request: ValidateKeyRequest): Promise<ValidateKeyResponse> => {
    const response = await api.post('/api/auth/validate', request);
    return response.data;
  },
};

export const modelsAPI = {
  listModels: async (request: ListModelsRequest) => {
    const response = await api.post('/api/models/list', request);
    return response.data;
  },
};

export const sessionsAPI = {
  create: async (name: string = 'New Session') => {
    const response = await api.post('/api/sessions', { name });
    return response.data;
  },
  list: async () => {
    const response = await api.get('/api/sessions');
    return response.data;
  },
  get: async (sessionId: number) => {
    const response = await api.get(`/api/sessions/${sessionId}`);
    return response.data;
  },
  getMessages: async (sessionId: number) => {
    const response = await api.get(`/api/sessions/${sessionId}/messages`);
    return response.data;
  },
  delete: async (sessionId: number) => {
    const response = await api.delete(`/api/sessions/${sessionId}`);
    return response.data;
  },
  rename: async (sessionId: number, name: string) => {
    const response = await api.patch(`/api/sessions/${sessionId}/rename`, { name });
    return response.data;
  },
  duplicate: async (sessionId: number) => {
    const response = await api.post(`/api/sessions/${sessionId}/duplicate`);
    return response.data;
  },
};

export const chatAPI = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/chat', request);
    return response.data;
  },
  sendMessageStream: async (
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onDone: (fullResponse: string) => void,
    onError: (error: string) => void,
    onSearchData?: (data: any) => void
  ): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      onError(error.detail || 'Streaming request failed');
      return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      onError('No response body');
      return;
    }

    let buffer = '';
    let fullResponse = '';
    let hasReceivedData = false;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          // If stream ends without any data, check if we have buffered data
          if (!hasReceivedData && buffer.trim()) {
            console.warn('Stream ended with buffered data:', buffer);
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine) continue; // Skip empty lines
          
          if (trimmedLine.startsWith('data: ')) {
            hasReceivedData = true;
            try {
              const jsonStr = trimmedLine.slice(6);
              const data = JSON.parse(jsonStr);
              
              if (data.type === 'chunk') {
                const content = data.content || '';
                fullResponse += content;
                onChunk(content);
              } else if (data.type === 'search_results' || data.type === 'tool_call') {
                if (onSearchData) {
                  onSearchData(data);
                }
              } else if (data.type === 'done') {
                onDone(data.content || fullResponse);
                return;
              } else if (data.type === 'error') {
                onError(data.content || 'Unknown error');
                return;
              } else {
                console.warn('Unknown SSE event type:', data.type);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, 'Line:', trimmedLine);
            }
          } else if (trimmedLine.startsWith('event:') || trimmedLine.startsWith('id:')) {
            // Skip other SSE fields for now
            continue;
          } else {
            console.warn('Unexpected SSE line format:', trimmedLine);
          }
        }
      }
      
      // If stream ended without a 'done' event, call onDone with accumulated response
      if (hasReceivedData && fullResponse) {
        onDone(fullResponse);
      } else if (!hasReceivedData) {
        onError('No data received from stream');
      }
    } catch (error: any) {
      console.error('Streaming error:', error);
      onError(error.message || 'Streaming error');
    }
  },
};

export const newsAPI = {
  processURLs: async (request: ProcessURLsRequest): Promise<ProcessedURL[]> => {
    const response = await api.post('/api/news/process-urls', request);
    return response.data;
  },
};

