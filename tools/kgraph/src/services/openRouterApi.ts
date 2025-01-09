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

interface OpenRouterUsage {
  data: {
    [modelId: string]: {
      input_tokens: number;
      output_tokens: number;
      requests: number;
    };
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
    // First get the models
    const modelsResponse = await openRouterApi.get<{ data: OpenRouterModel[] }>('/models');
    
    // Try to get usage data, but don't fail if it's not available
    let modelUsage: OpenRouterUsage['data'] = {};
    try {
      console.log('Fetching usage data...');
      const usageResponse = await openRouterApi.get<OpenRouterUsage>('/usage');
      console.log('Usage response:', usageResponse);
      
      if (usageResponse.data && usageResponse.data.data) {
        modelUsage = usageResponse.data.data;
        console.log('Parsed usage data:', modelUsage);
      } else {
        console.warn('Usage data missing expected structure:', usageResponse.data);
      }
    } catch (error) {
      console.warn('Could not fetch usage data:', error);
      if (axios.isAxiosError(error)) {
        console.warn('Response:', error.response?.data);
        console.warn('Status:', error.response?.status);
      }
    }
    
    return modelsResponse.data.data.map((model: OpenRouterModel) => ({
      id: model.id,
      name: model.name,
      provider: model.id.split('/')[0],
      context_length: model.context_length,
      popularity: modelUsage[model.id]?.requests || 0
    }));
  } catch (error) {
    console.error('Error fetching OpenRouter data:', error);
    throw error;
  }
};

export default openRouterApi;
