import axios from 'axios';
import type { AIModel } from '../store/slices/uiSlice';

const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1';

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
    console.error('Error fetching OpenRouter models:', error);
    throw error;
  }
};

export default openRouterApi;
