import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { AppState, Node, Graph, Viewport, ActionTypes, Theme } from '../types';

const initialState: AppState = {
  viewport: {
    zoom: 1,
    position: { x: 0, y: 0 }
  },
  graphs: [],
  currentGraph: null,
  selectedNode: null,
  error: null,
  theme: 'light',
  chatSession: {
    isActive: false,
    messages: []
  }
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    // App Actions
    openGraph: (state, action: PayloadAction<string>) => {
      const graph = state.graphs.find(g => g.id === action.payload);
      if (graph) {
        state.currentGraph = graph;
        state.selectedNode = null;
        state.error = null;
      }
    },
    createGraph: (state, action: PayloadAction<{ title: string }>) => {
      const newGraph: Graph = {
        id: Date.now().toString(),
        title: action.payload.title,
        nodes: [],
        edges: []
      };
      state.graphs.push(newGraph);
      state.currentGraph = newGraph;
      state.selectedNode = null;
    },
    deleteGraph: (state, action: PayloadAction<string>) => {
      state.graphs = state.graphs.filter(g => g.id !== action.payload);
      if (state.currentGraph?.id === action.payload) {
        state.currentGraph = null;
        state.selectedNode = null;
      }
    },
    clearAll: (state) => {
      state.graphs = [];
      state.currentGraph = null;
      state.selectedNode = null;
      state.error = null;
      state.chatSession = { isActive: false, messages: [] };
    },

    // Node Actions
    createNode: (state, action: PayloadAction<{ label: string; position: { x: number; y: number } }>) => {
      if (state.currentGraph) {
        const newNode: Node = {
          id: Date.now().toString(),
          label: action.payload.label,
          position: action.payload.position,
          properties: {}
        };
        state.currentGraph.nodes.push(newNode);
        state.selectedNode = newNode;
      }
    },
    selectNode: (state, action: PayloadAction<string>) => {
      if (state.currentGraph) {
        state.selectedNode = state.currentGraph.nodes.find(n => n.id === action.payload) || null;
      }
    },
    editNode: (state, action: PayloadAction<{ id: string; changes: Partial<Node> }>) => {
      if (state.currentGraph) {
        const node = state.currentGraph.nodes.find(n => n.id === action.payload.id);
        if (node) {
          Object.assign(node, action.payload.changes);
          if (state.selectedNode?.id === node.id) {
            state.selectedNode = node;
          }
        }
      }
    },
    moveNode: (state, action: PayloadAction<{ id: string; position: { x: number; y: number } }>) => {
      if (state.currentGraph) {
        const node = state.currentGraph.nodes.find(n => n.id === action.payload.id);
        if (node) {
          node.position = action.payload.position;
        }
      }
    },
    connectNodes: (state, action: PayloadAction<{ source: string; target: string; label?: string }>) => {
      if (state.currentGraph) {
        state.currentGraph.edges.push({
          id: Date.now().toString(),
          source: action.payload.source,
          target: action.payload.target,
          label: action.payload.label
        });
      }
    },
    deleteNode: (state, action: PayloadAction<string>) => {
      if (state.currentGraph) {
        state.currentGraph.nodes = state.currentGraph.nodes.filter(n => n.id !== action.payload);
        state.currentGraph.edges = state.currentGraph.edges.filter(
          e => e.source !== action.payload && e.target !== action.payload
        );
        if (state.selectedNode?.id === action.payload) {
          state.selectedNode = null;
        }
      }
    },
    deselectNode: (state) => {
      state.selectedNode = null;
    },

    // Chat Actions
    openChat: (state) => {
      state.chatSession.isActive = true;
    },
    closeChat: (state) => {
      state.chatSession.isActive = false;
    },
    addMessage: (state, action: PayloadAction<{ role: 'user' | 'assistant'; content: string }>) => {
      state.chatSession.messages.push(action.payload);
    },

    // Error Actions
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },

    // Theme Actions
    setTheme: (state, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
      document.documentElement.setAttribute('data-theme', action.payload);
    },

    // Viewport Actions
    updateViewport: (state, action: PayloadAction<Partial<Viewport>>) => {
      state.viewport = { ...state.viewport, ...action.payload };
    }
  }
});

export const {
  openGraph,
  createGraph,
  deleteGraph,
  clearAll,
  createNode,
  selectNode,
  editNode,
  moveNode,
  connectNodes,
  deleteNode,
  deselectNode,
  openChat,
  closeChat,
  addMessage,
  setError,
  clearError,
  setTheme,
  updateViewport
} = appSlice.actions;

export default appSlice.reducer;
