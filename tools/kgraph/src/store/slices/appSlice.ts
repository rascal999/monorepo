import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { AppState, Node, Graph, Viewport, Theme } from '../types';
import { createAction } from '@reduxjs/toolkit';
import { REHYDRATE } from 'redux-persist';

// Create action for loading graph
export const loadGraph = createAction<string>('app/loadGraph');

const initialState: AppState = {
  graphs: [],
  currentGraph: null,
  selectedNode: null,
  error: null,
  theme: 'light',
  loading: {
    graphId: null,
    status: false
  },
  panelWidth: 400
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    rehydrateComplete: (state, action: PayloadAction<AppState>) => {
      return {
        ...state,
        ...action.payload,
        loading: { graphId: null, status: false }
      };
    },
    restoreState: (state, action: PayloadAction<Partial<AppState>>) => {
      if (action.payload.graphs) {
        state.graphs = action.payload.graphs;
      }
      if (action.payload.currentGraph) {
        state.currentGraph = action.payload.currentGraph;
      }
    },
    // Loading Actions
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

    // App Actions
    loadGraphSuccess: (state, action: PayloadAction<Graph>) => {
      state.currentGraph = action.payload;
      state.error = null;
      state.loading = {
        graphId: null,
        status: false
      };
      
      // Focus on last focused node or first node
      if (action.payload.nodes.length > 0) {
        const nodeToFocus = action.payload.lastFocusedNodeId 
          ? action.payload.nodes.find(n => n.id === action.payload.lastFocusedNodeId)
          : action.payload.nodes[0];
        
        state.selectedNode = nodeToFocus || null;
      } else {
        state.selectedNode = null;
      }
    },
    createGraph: (state, action: PayloadAction<{ title: string }>) => {
      const newGraph: Graph = {
        id: Date.now().toString(),
        title: action.payload.title,
        nodes: [],
        edges: [],
        viewport: {
          zoom: 1,
          position: { x: 0, y: 0 }
        },
        lastFocusedNodeId: undefined
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
        // Add node to both currentGraph and the graph in graphs array
        state.currentGraph.nodes.push(newNode);
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        if (graphInArray) {
          graphInArray.nodes.push(newNode);
        }
        state.selectedNode = newNode;
        // Initialize chat history
        newNode.properties.chatHistory = [];
        
        // Set as last focused node
        state.currentGraph.lastFocusedNodeId = newNode.id;
        if (graphInArray) {
          graphInArray.lastFocusedNodeId = newNode.id;
        }
      }
    },
    selectNode: (state, action: PayloadAction<string>) => {
      if (state.currentGraph) {
        const node = state.currentGraph.nodes.find(n => n.id === action.payload);
        state.selectedNode = node || null;
        
        if (node) {
          // Update lastFocusedNodeId in both currentGraph and graphs array
          state.currentGraph.lastFocusedNodeId = node.id;
          const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
          if (graphInArray) {
            graphInArray.lastFocusedNodeId = node.id;
          }
        }
      }
    },
    editNode: (state, action: PayloadAction<{ id: string; changes: Partial<Node> }>) => {
      if (state.currentGraph) {
        const node = state.currentGraph.nodes.find(n => n.id === action.payload.id);
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        const nodeInArray = graphInArray?.nodes.find(n => n.id === action.payload.id);
        
        if (node) {
          Object.assign(node, action.payload.changes);
          if (nodeInArray) {
            Object.assign(nodeInArray, action.payload.changes);
          }
          if (state.selectedNode?.id === node.id) {
            state.selectedNode = node;
          }
        }
      }
    },
    moveNode: (state, action: PayloadAction<{ id: string; position: { x: number; y: number } }>) => {
      if (state.currentGraph) {
        const node = state.currentGraph.nodes.find(n => n.id === action.payload.id);
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        const nodeInArray = graphInArray?.nodes.find(n => n.id === action.payload.id);
        
        if (node) {
          node.position = action.payload.position;
          if (nodeInArray) {
            nodeInArray.position = action.payload.position;
          }
        }
      }
    },
    connectNodes: (state, action: PayloadAction<{ source: string; target: string; label?: string }>) => {
      if (state.currentGraph) {
        const newEdge = {
          id: Date.now().toString(),
          source: action.payload.source,
          target: action.payload.target,
          label: action.payload.label
        };
        state.currentGraph.edges.push(newEdge);
        
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        if (graphInArray) {
          graphInArray.edges.push(newEdge);
        }
      }
    },
    deleteNode: (state, action: PayloadAction<string>) => {
      if (state.currentGraph) {
        state.currentGraph.nodes = state.currentGraph.nodes.filter(n => n.id !== action.payload);
        state.currentGraph.edges = state.currentGraph.edges.filter(
          e => e.source !== action.payload && e.target !== action.payload
        );
        
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        if (graphInArray) {
          graphInArray.nodes = graphInArray.nodes.filter(n => n.id !== action.payload);
          graphInArray.edges = graphInArray.edges.filter(
            e => e.source !== action.payload && e.target !== action.payload
          );
        }
        
        if (state.selectedNode?.id === action.payload) {
          state.selectedNode = null;
        }
        
        // Clear lastFocusedNodeId if it was this node
        if (state.currentGraph.lastFocusedNodeId === action.payload) {
          state.currentGraph.lastFocusedNodeId = undefined;
          if (graphInArray) {
            graphInArray.lastFocusedNodeId = undefined;
          }
        }
      }
    },
    deselectNode: (state) => {
      state.selectedNode = null;
    },

    // Chat Actions
    addMessage: (state, action: PayloadAction<{ nodeId: string; role: 'user' | 'assistant'; content: string }>) => {
      if (state.currentGraph) {
        const node = state.currentGraph.nodes.find(n => n.id === action.payload.nodeId);
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        const nodeInArray = graphInArray?.nodes.find(n => n.id === action.payload.nodeId);
        
        if (node) {
          if (!node.properties.chatHistory) {
            node.properties.chatHistory = [];
          }
          node.properties.chatHistory.push({
            role: action.payload.role,
            content: action.payload.content
          });
          
          if (nodeInArray) {
            if (!nodeInArray.properties.chatHistory) {
              nodeInArray.properties.chatHistory = [];
            }
            nodeInArray.properties.chatHistory.push({
              role: action.payload.role,
              content: action.payload.content
            });
          }
        }
      }
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

    // Panel Actions
    updatePanelWidth: (state, action: PayloadAction<number>) => {
      state.panelWidth = action.payload;
    },

    // Graph Viewport Actions
    updateGraphViewport: (state, action: PayloadAction<Partial<Viewport>>) => {
      if (state.currentGraph) {
        state.currentGraph.viewport = { 
          ...state.currentGraph.viewport, 
          ...action.payload 
        };
        // Update viewport in graphs array too
        const graphInArray = state.graphs.find(g => g.id === state.currentGraph!.id);
        if (graphInArray) {
          graphInArray.viewport = { 
            ...graphInArray.viewport, 
            ...action.payload 
          };
        }
      }
    }
  },
  extraReducers: (builder) => {
    builder.addCase(REHYDRATE, (state, action: any) => {
      if (action.payload && action.key === 'kgraph') {
        return {
          ...state,
          ...action.payload,
          loading: { graphId: null, status: false }
        };
      }
      return state;
    });
  }
});

export const {
  rehydrateComplete,
  restoreState,
  loadGraphSuccess,
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
  addMessage,
  setError,
  clearError,
  setTheme,
  setLoading,
  clearLoading,
  updatePanelWidth,
  updateGraphViewport
} = appSlice.actions;

export default appSlice.reducer;
