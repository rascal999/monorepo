import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import type { Graph, Node } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatState {
  // No local state needed as chat history is stored in node properties
}

const initialState: ChatState = {};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
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
  addMessage
} = chatSlice.actions;

export default chatSlice.reducer;
