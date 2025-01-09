import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import type { Graph, Node } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatState {
  streaming: {
    nodeId: string | null;
    inProgress: boolean;
    error: string | null;
    currentResponse: string;
  };
}

const initialState: ChatState = {
  streaming: {
    nodeId: null,
    inProgress: false,
    error: null,
    currentResponse: ''
  }
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    startStreaming: (state, action: PayloadAction<{ nodeId: string }>) => {
      state.streaming = {
        nodeId: action.payload.nodeId,
        inProgress: true,
        error: null,
        currentResponse: ''
      };
    },
    appendStreamChunk: (state, action: PayloadAction<{
      nodeId: string;
      content: string;
    }>) => {
      if (state.streaming.nodeId === action.payload.nodeId) {
        state.streaming.currentResponse += action.payload.content;
      }
    },
    endStreaming: (state) => {
      state.streaming = {
        nodeId: null,
        inProgress: false,
        error: null,
        currentResponse: ''
      };
    },
    setStreamingError: (state, action: PayloadAction<string>) => {
      state.streaming = {
        ...state.streaming,
        inProgress: false,
        error: action.payload
      };
    },
    addMessage: {
      reducer: (state, action: PayloadAction<{
        nodeId: string;
        role: 'user' | 'assistant';
        content: string;
      }>) => {
        // State updates are handled by the prepare callback
      },
      prepare: (params: {
        nodeId: string;
        role: 'user' | 'assistant';
        content: string;
      }) => {
        return {
          payload: params,
          meta: {
            updateNode: true // Signal that this action should trigger a node update
          }
        };
      }
    }
  }
});

export const {
  addMessage,
  startStreaming,
  appendStreamChunk,
  endStreaming,
  setStreamingError
} = chatSlice.actions;

export default chatSlice.reducer;
