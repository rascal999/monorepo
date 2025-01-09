import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { Theme } from '../types';

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  context_length?: number;
}

export interface UIState {
  theme: Theme;
  aiModels: AIModel[];
  selectedModel: string;
  modelSearchQuery: string;
  modelsLoading: boolean;
  modelsError: string | null;
  loading: {
    graphId: string | null;
    status: boolean;
  };
  error: string | null;
  settingsOpen: boolean;
  settingsTab: 'general';
}

const defaultModels: AIModel[] = [
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI' },
  { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI' },
  { id: 'claude-2', name: 'Claude 2', provider: 'Anthropic' }
];

const initialState: UIState = {
  theme: 'light',
  aiModels: defaultModels,
  selectedModel: 'gpt-3.5-turbo',
  modelSearchQuery: '',
  modelsLoading: false,
  modelsError: null,
  loading: {
    graphId: null,
    status: false
  },
  error: null,
  settingsOpen: false,
  settingsTab: 'general'
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
      document.documentElement.setAttribute('data-theme', action.payload);
    },
    setAIModel: (state, action: PayloadAction<string>) => {
      state.selectedModel = action.payload;
    },
    setAIModels: (state, action: PayloadAction<AIModel[]>) => {
      state.aiModels = action.payload;
    },
    setModelSearchQuery: (state, action: PayloadAction<string>) => {
      state.modelSearchQuery = action.payload;
    },
    fetchModelsStart: (state) => {
      state.modelsLoading = true;
      state.modelsError = null;
    },
    fetchModelsSuccess: (state, action: PayloadAction<AIModel[]>) => {
      state.aiModels = action.payload;
      state.modelsLoading = false;
      state.modelsError = null;
    },
    fetchModelsFailure: (state, action: PayloadAction<string>) => {
      state.modelsLoading = false;
      state.modelsError = action.payload;
    },
    openSettings: (state) => {
      state.settingsOpen = true;
    },
    closeSettings: (state) => {
      state.settingsOpen = false;
    },
    setSettingsTab: (state, action: PayloadAction<'general'>) => {
      state.settingsTab = action.payload;
    },
    setLoading: (state, action: PayloadAction<string>) => {
      state.loading = {
        graphId: action.payload,
        status: true
      };
    },
    clearLoading: (state) => {
      state.loading = {
        graphId: null,
        status: false
      };
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  }
});

export const {
  setTheme,
  setAIModel,
  setAIModels,
  setModelSearchQuery,
  fetchModelsStart,
  fetchModelsSuccess,
  fetchModelsFailure,
  openSettings,
  closeSettings,
  setSettingsTab,
  setLoading,
  clearLoading,
  setError,
  clearError
} = uiSlice.actions;

export default uiSlice.reducer;
