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
      const newState = {
        ...state,
        ...action.payload
      };
      return newState;
    },
    restoreState: (state, action: PayloadAction<Partial<GraphState>>) => {
      if (action.payload.graphs) {
        state.graphs = action.payload.graphs;
      }
      if (action.payload.currentGraph) {
        state.currentGraph = action.payload.currentGraph;
      }
    },
    loadGraphSuccess: (state, action: PayloadAction<Graph>) => {
      state.currentGraph = action.payload;
    },
    createGraph: {
      reducer: (state, action: PayloadAction<{ title: string; id: string }>) => {
        const newGraph: Graph = {
          id: action.payload.id,
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
      },
      prepare: (params: { title: string }) => {
        const id = Date.now().toString();
        return { payload: { ...params, id } };
      }
    },
    addNode: (state, action: PayloadAction<{ graphId: string; node: Node }>) => {
      const { graphId, node } = action.payload;
      
      // Add to currentGraph if it matches
      if (state.currentGraph?.id === graphId) {
        state.currentGraph.nodes.push(node);
        state.currentGraph.lastFocusedNodeId = node.id;
      }
      
      // Add to graphs array
      const graphInArray = state.graphs.find(g => g.id === graphId);
      if (graphInArray) {
        graphInArray.nodes.push(node);
        graphInArray.lastFocusedNodeId = node.id;
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
      if (state.currentGraph) {
        // Update viewport
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
    },
    updateNodeInGraph: (state, action: PayloadAction<{
      nodeId: string;
      changes: Partial<Node>;
    }>) => {
      console.log('graphSlice: Updating node in graph', {
        currentGraph: state.currentGraph ? {
          id: state.currentGraph.id,
          nodeCount: state.currentGraph.nodes.length
        } : null,
        nodeId: action.payload.nodeId,
        changeType: action.payload.changes.properties ? 'properties' : 'other'
      });

      if (!state.currentGraph) {
        console.warn('graphSlice: No current graph');
        return;
      }

      // Update node in current graph
      const nodeIndex = state.currentGraph.nodes.findIndex(n => n.id === action.payload.nodeId);
      console.log('graphSlice: Found node index in current graph', {
        nodeId: action.payload.nodeId,
        nodeIndex,
        found: nodeIndex !== -1
      });

      if (nodeIndex !== -1) {
        const currentNode = state.currentGraph.nodes[nodeIndex];
        const updatedNode = {
          ...currentNode,
          ...action.payload.changes,
          properties: {
            ...currentNode.properties,
            ...(action.payload.changes.properties || {})
          }
        };
        console.log('graphSlice: Updating node in current graph', {
          nodeId: currentNode.id,
          label: currentNode.label,
          hasProperties: Boolean(currentNode.properties),
          chatHistoryLength: currentNode.properties?.chatHistory?.length || 0
        });
        state.currentGraph.nodes[nodeIndex] = updatedNode;
      }

      // Update node in graphs array
      const graphIndex = state.graphs.findIndex(g => g.id === state.currentGraph!.id);
      if (graphIndex !== -1) {
        const nodeIndex = state.graphs[graphIndex].nodes.findIndex(n => n.id === action.payload.nodeId);
        if (nodeIndex !== -1) {
          const currentNode = state.graphs[graphIndex].nodes[nodeIndex];
          const updatedNode = {
            ...currentNode,
            ...action.payload.changes,
            properties: {
              ...currentNode.properties,
              ...(action.payload.changes.properties || {})
            }
          };
          state.graphs[graphIndex].nodes[nodeIndex] = updatedNode;
        }
      }
    }
  },
  extraReducers: (builder) => {
    builder.addCase(REHYDRATE, (state, action: any) => {
      if (action.payload && action.key === 'kgraph') {
        const newState = {
          ...state,
          ...action.payload
        };
        return newState;
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
  updateGraphViewport,
  addNode,
  updateNodeInGraph
} = graphSlice.actions;

export default graphSlice.reducer;
