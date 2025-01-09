import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { Theme } from '../types';

export type AIModel = 'gpt-3.5-turbo' | 'gpt-4' | 'claude-2';

export interface UIState {
  theme: Theme;
  aiModel: AIModel;
  loading: {
    graphId: string | null;
    status: boolean;
  };
  error: string | null;
  settingsOpen: boolean;
  settingsTab: 'general';
}

const initialState: UIState = {
  theme: 'light',
  aiModel: 'gpt-3.5-turbo',
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
    setAIModel: (state, action: PayloadAction<AIModel>) => {
      state.aiModel = action.payload;
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
  openSettings,
  closeSettings,
  setSettingsTab,
  setLoading,
  clearLoading,
  setError,
  clearError
} = uiSlice.actions;

export default uiSlice.reducer;
