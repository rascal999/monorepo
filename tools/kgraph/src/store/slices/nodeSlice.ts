import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { Node } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface NodeState {
  selectedNode: Node | null;
}

const initialState: NodeState = {
  selectedNode: null
};

const nodeSlice = createSlice({
  name: 'node',
  initialState,
  reducers: {
    createNode: {
      reducer: (state, action: PayloadAction<{ 
        graphId: string;
        label: string; 
        position: { x: number; y: number };
        nodeId: string;
      }>) => {
        const newNode: Node = {
          id: action.payload.nodeId,
          label: action.payload.label,
          position: action.payload.position,
          properties: {
            chatHistory: []
          }
        };
        
        // Set as selected node and ensure it's properly initialized
        state.selectedNode = {
          ...newNode,
          properties: {
            chatHistory: []
          }
        };
        console.log('nodeSlice: Created and selected node', {
          nodeId: newNode.id,
          label: newNode.label
        });
      },
      prepare: (params: {
        graphId: string;
        label: string;
        position: { x: number; y: number };
      }) => {
        return {
          payload: {
            ...params,
            nodeId: Date.now().toString()
          },
          meta: {
            updateGraph: true // Signal that this action should trigger a graph update
          }
        };
      }
    },
    selectNode: {
      reducer: (state, action: PayloadAction<{ node: Node | null }>) => {
        state.selectedNode = action.payload.node;
      },
      prepare: (params: { node: Node | null }) => {
        return {
          payload: params,
          meta: {
            updateGraph: true
          }
        };
      }
    },
    editNode: {
      reducer: (state, action: PayloadAction<{ 
        id: string;
        changes: Partial<Node>;
      }>) => {
        // Update selected node if it matches
        if (state.selectedNode?.id === action.payload.id) {
          state.selectedNode = {
            ...state.selectedNode,
            ...action.payload.changes
          };
        }
      },
      prepare: (params: { id: string; changes: Partial<Node> }) => {
        return {
          payload: params,
          meta: {
            updateGraph: true
          }
        };
      }
    },
    moveNode: {
      reducer: (state, action: PayloadAction<{
        id: string;
        position: { x: number; y: number };
      }>) => {
        // Update selected node position if it matches
        if (state.selectedNode?.id === action.payload.id) {
          state.selectedNode.position = action.payload.position;
        }
      },
      prepare: (params: { id: string; position: { x: number; y: number } }) => {
        return {
          payload: params,
          meta: {
            updateGraph: true
          }
        };
      }
    },
    updateNodeChatHistory: {
      reducer: (state, action: PayloadAction<{
        nodeId: string;
        message: { role: 'user' | 'assistant'; content: string };
      }>) => {
        console.log('nodeSlice: Updating chat history', {
          selectedNodeId: state.selectedNode?.id,
          messageNodeId: action.payload.nodeId,
          messageRole: action.payload.message.role,
          currentChatLength: state.selectedNode?.properties.chatHistory?.length || 0
        });

        if (!state.selectedNode) {
          console.warn('nodeSlice: No selected node');
          return;
        }

        if (state.selectedNode.id !== action.payload.nodeId) {
          console.warn('nodeSlice: Selected node ID does not match payload node ID', {
            selectedNodeId: state.selectedNode.id,
            payloadNodeId: action.payload.nodeId
          });
          return;
        }

        const chatHistory = state.selectedNode.properties.chatHistory || [];
        const newChatHistory = action.payload.message.role === 'user' && chatHistory.length === 0
          ? [action.payload.message] // Keep first user message in history but don't display it
          : [...chatHistory, action.payload.message];

        console.log('nodeSlice: Updating chat history', {
          oldLength: chatHistory.length,
          newLength: newChatHistory.length,
          lastMessage: action.payload.message.role,
          isFirstUserMessage: action.payload.message.role === 'user' && chatHistory.length === 0
        });

        state.selectedNode = {
          ...state.selectedNode,
          properties: {
            ...state.selectedNode.properties,
            chatHistory: newChatHistory
          }
        };
      },
      prepare: (params: { nodeId: string; message: { role: 'user' | 'assistant'; content: string } }) => {
        return {
          payload: params,
          meta: {
            updateGraph: true
          }
        };
      }
    },
    connectNodes: {
      reducer: (state, action: PayloadAction<{
        source: string;
        target: string;
        label?: string;
      }>) => {
        // No local state to update
      },
      prepare: (params: { source: string; target: string; label?: string }) => {
        return {
          payload: params,
          meta: {
            updateGraph: true
          }
        };
      }
    },
    deleteNode: {
      reducer: (state, action: PayloadAction<{ nodeId: string }>) => {
        if (state.selectedNode?.id === action.payload.nodeId) {
          state.selectedNode = null;
        }
      },
      prepare: (params: { nodeId: string }) => {
        return {
          payload: params,
          meta: {
            updateGraph: true
          }
        };
      }
    },
    deselectNode: (state) => {
      state.selectedNode = null;
    },
    createWordNode: {
      reducer: (state, action: PayloadAction<{
        parentNodeId: string;
        word: string;
        position: { x: number; y: number };
        nodeId: string;
      }>) => {
        const newNode: Node = {
          id: action.payload.nodeId,
          label: action.payload.word,
          position: action.payload.position,
          properties: {
            chatHistory: []
          }
        };
        
        // Set as selected node
        state.selectedNode = newNode;
        
        console.log('nodeSlice: Created word node', {
          nodeId: newNode.id,
          label: newNode.label,
          parentNodeId: action.payload.parentNodeId
        });
      },
      prepare: (params: {
        parentNodeId: string;
        word: string;
        position: { x: number; y: number };
        graphId: string;  // Make graphId required
      }) => {
        const nodeId = Date.now().toString();
        return {
          payload: {
            ...params,
            nodeId
          },
          meta: {
            updateGraph: true,
            createConnection: true // Signal that we need to create a connection to parent
          }
        };
      }
    }
  }
});

export const {
  createNode,
  selectNode,
  editNode,
  moveNode,
  connectNodes,
  deleteNode,
  deselectNode,
  updateNodeChatHistory,
  createWordNode
} = nodeSlice.actions;

export default nodeSlice.reducer;
