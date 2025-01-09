import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { Theme } from '../types';

export interface UIState {
  theme: Theme;
  loading: {
    graphId: string | null;
    status: boolean;
  };
  error: string | null;
}

const initialState: UIState = {
  theme: 'light',
  loading: {
    graphId: null,
    status: false
  },
  error: null
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
      document.documentElement.setAttribute('data-theme', action.payload);
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
  setLoading,
  clearLoading,
  setError,
  clearError
} = uiSlice.actions;

export default uiSlice.reducer;
