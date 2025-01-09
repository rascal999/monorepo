import axios from 'axios';
import type { AIModel } from '../store/slices/uiSlice';

const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1';
const CHAT_COMPLETION_URL = `${OPENROUTER_API_URL}/chat/completions`;

interface OpenRouterModel {
  id: string;
  name: string;
  context_length: number;
  pricing: {
    prompt: string;
    completion: string;
  };
}

const openRouterApi = axios.create({
  baseURL: OPENROUTER_API_URL,
  headers: {
    'Authorization': `Bearer ${import.meta.env.VITE_OPENROUTER_API_KEY}`,
    'HTTP-Referer': window.location.origin,
    'X-Title': window.location.pathname
  }
});

export const fetchModels = async (): Promise<AIModel[]> => {
  try {
    const response = await openRouterApi.get<{ data: OpenRouterModel[] }>('/models');
    return response.data.data.map((model: OpenRouterModel) => ({
      id: model.id,
      name: model.name,
      provider: model.id.split('/')[0],
      context_length: model.context_length
    }));
  } catch (error) {
    console.error('Error fetching OpenRouter data:', error);
    throw error;
  }
};

export interface ChatCompletionOptions {
  model: string;
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
  }>;
  stream?: boolean;
  temperature?: number;
  max_tokens?: number;
}

export const streamChatCompletion = async (
  options: ChatCompletionOptions,
  onChunk: (chunk: string) => void,
  onError: (error: Error) => void,
  onComplete: () => void
) => {
  try {
    const response = await fetch(CHAT_COMPLETION_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${import.meta.env.VITE_OPENROUTER_API_KEY}`,
        'HTTP-Referer': window.location.origin,
        'X-Title': window.location.pathname,
      },
      body: JSON.stringify({
        ...options,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.error?.message || errorMessage;
      } catch (e) {
        // If error text is not JSON, use it directly
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is null');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim() === '') continue;
        if (line.trim() === 'data: [DONE]') {
          onComplete();
          continue;
        }
        if (!line.startsWith('data: ')) continue;

        try {
          const json = JSON.parse(line.slice(6));
          const content = json.choices[0]?.delta?.content;
          if (content) {
            onChunk(content);
          }
        } catch (e) {
          console.error('Error parsing SSE message:', e);
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error : new Error(String(error)));
  }
};

export default openRouterApi;
