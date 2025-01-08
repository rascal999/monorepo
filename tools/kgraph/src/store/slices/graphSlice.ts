import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { createAction } from '@reduxjs/toolkit';
import { REHYDRATE } from 'redux-persist';
import type { Graph, Node, Viewport } from '../types';

// Create action for loading graph
export const loadGraph = createAction<string>('graph/loadGraph');

export interface GraphState {
  graphs: Graph[];
  currentGraph: Graph | null;
  meta?: {
    newGraphId?: string;
  };
}

const initialState: GraphState = {
  graphs: [],
  currentGraph: null,
  meta: {}
};

const graphSlice = createSlice({
  name: 'graph',
  initialState,
  reducers: {
    rehydrateComplete: (state, action: PayloadAction<GraphState>) => {
      // First restore graphs array
      state.graphs = action.payload.graphs || [];
      
      // Then set currentGraph to reference the correct graph in the array
      if (action.payload.currentGraph) {
        const graphIndex = state.graphs.findIndex(g => g.id === action.payload.currentGraph!.id);
        if (graphIndex === -1) {
          console.warn('graphSlice: Current graph not found in rehydrated graphs');
          state.currentGraph = null;
        } else {
          state.currentGraph = state.graphs[graphIndex];
        }
      } else {
        state.currentGraph = null;
      }
      
      // Restore meta
      state.meta = action.payload.meta || {};
    },
    restoreState: (state, action: PayloadAction<Partial<GraphState>>) => {
      if (action.payload.graphs) {
        state.graphs = action.payload.graphs;
      }
      if (action.payload.currentGraph) {
        // Find the graph in the restored graphs array
        const graphIndex = state.graphs.findIndex(g => g.id === action.payload.currentGraph!.id);
        if (graphIndex === -1) {
          console.warn('graphSlice: Current graph not found in restored graphs');
          state.currentGraph = null;
        } else {
          // Set currentGraph to reference the graph in the array
          state.currentGraph = state.graphs[graphIndex];
        }
      }
    },
    loadGraphSuccess: (state, action: PayloadAction<Graph>) => {
      // Find the graph in the graphs array
      const graphIndex = state.graphs.findIndex(g => g.id === action.payload.id);
      if (graphIndex === -1) {
        console.warn('graphSlice: Graph not found in graphs array');
        return;
      }
      
      // Set currentGraph to reference the graph in the array
      state.currentGraph = state.graphs[graphIndex];
    },
    createGraph: {
      reducer: (state, action: PayloadAction<{ title: string; id: string }>) => {
        // Initialize viewport with zoom, position will be set by Cytoscape's center()
        const initialViewport = {
          zoom: 0.75,
          position: { x: 0, y: 0 }
        };

        // Create new graph
        const newGraph: Graph = {
          id: action.payload.id,
          title: action.payload.title,
          nodes: [],
          edges: [],
          viewport: initialViewport,
          lastFocusedNodeId: undefined
        };

        // Add to graphs array
        state.graphs.push(newGraph);
        
        // Set currentGraph to reference the graph in the array
        const graphIndex = state.graphs.length - 1;
        state.currentGraph = state.graphs[graphIndex];
      },
      prepare: (params: { title: string }) => {
        const id = Date.now().toString();
        return { payload: { ...params, id } };
      }
    },
    addNode: (state, action: PayloadAction<{ graphId: string; node: Node }>) => {
      const { graphId, node } = action.payload;
      
      // Find the graph in the graphs array
      const graphIndex = state.graphs.findIndex(g => g.id === graphId);
      if (graphIndex === -1) {
        console.warn('graphSlice: Graph not found in graphs array');
        return;
      }
      
      // Add node to graph in graphs array
      state.graphs[graphIndex].nodes.push(node);
      state.graphs[graphIndex].lastFocusedNodeId = node.id;
      
      // Update currentGraph reference if it matches
      if (state.currentGraph?.id === graphId) {
        state.currentGraph = state.graphs[graphIndex];
        
        // If this is the first node, ensure it's focused
        if (state.currentGraph.nodes.length === 1) {
          console.log('graphSlice: First node added, ensuring focus', {
            nodeId: node.id,
            graphId: graphId
          });
          // The node will be focused by the selectNode action dispatched after this
        }
      }
    },
    deleteGraph: (state, action: PayloadAction<string>) => {
      state.graphs = state.graphs.filter(g => g.id !== action.payload);
      if (state.currentGraph?.id === action.payload) {
        state.currentGraph = null;
      }
    },
    clearAll: (state) => {
      state.graphs = [];
      state.currentGraph = null;
    },
    updateGraphViewport: (state, action: PayloadAction<Partial<Viewport>>) => {
      if (!state.currentGraph) {
        console.warn('graphSlice: No current graph');
        return;
      }

      // Find the graph in the graphs array
      const graphIndex = state.graphs.findIndex(g => g.id === state.currentGraph!.id);
      if (graphIndex === -1) {
        console.warn('graphSlice: Graph not found in graphs array');
        return;
      }

      // Update viewport in graphs array
      state.graphs[graphIndex].viewport = {
        ...state.graphs[graphIndex].viewport,
        ...action.payload
      };

      // Update currentGraph reference
      state.currentGraph = state.graphs[graphIndex];
    },
    updateNodeInGraph: (state, action: PayloadAction<{
      nodeId: string;
      changes: Partial<Node>;
    }>) => {
      if (!state.currentGraph) {
        console.warn('graphSlice: No current graph');
        return;
      }

      // Find the graph in the graphs array first
      const graphIndex = state.graphs.findIndex(g => g.id === state.currentGraph!.id);
      if (graphIndex === -1) {
        console.warn('graphSlice: Graph not found in graphs array');
        return;
      }

      // Update node in graphs array
      const nodeIndex = state.graphs[graphIndex].nodes.findIndex(n => n.id === action.payload.nodeId);
      if (nodeIndex === -1) {
        console.warn('graphSlice: Node not found in graph');
        return;
      }

      const currentNode = state.graphs[graphIndex].nodes[nodeIndex];
      const updatedNode = {
        ...currentNode,
        ...action.payload.changes,
        properties: {
          ...currentNode.properties,
          ...(action.payload.changes.properties || {})
        }
      };

      // Update in graphs array
      state.graphs[graphIndex].nodes[nodeIndex] = updatedNode;
      
      // Update currentGraph reference to point to the updated graph
      state.currentGraph = state.graphs[graphIndex];
    }
  },
  extraReducers: (builder) => {
    builder.addCase(REHYDRATE, (state, action: any) => {
      if (action.payload && action.key === 'kgraph') {
        // First restore graphs array
        state.graphs = action.payload.graphs || [];
        
        // Then set currentGraph to reference the correct graph in the array
        if (action.payload.currentGraph) {
          const graphIndex = state.graphs.findIndex(g => g.id === action.payload.currentGraph.id);
          if (graphIndex === -1) {
            console.warn('graphSlice: Current graph not found in rehydrated graphs');
            state.currentGraph = null;
          } else {
            state.currentGraph = state.graphs[graphIndex];
          }
        } else {
          state.currentGraph = null;
        }
        
        // Restore meta
        state.meta = action.payload.meta || {};
      }
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
  updateGraphViewport,
  addNode,
  updateNodeInGraph
} = graphSlice.actions;

export default graphSlice.reducer;
