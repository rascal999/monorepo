import { takeEvery, select, all, put, call } from 'redux-saga/effects';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Graph, Node } from '../types';
import { addNode, addEdge, updateNodePosition } from '../slices/graphSlice';
import { addMessage } from '../slices/chatSlice';
import { REHYDRATE } from 'redux-persist';
import cytoscape from 'cytoscape';
import { defaultColors } from '../../components/graph/GraphStyles';

// Selector to get current graph
const getCurrentGraph = (state: { graph: { currentGraph: Graph | null } }) => state.graph.currentGraph;

// Handle node selection
function* handleNodeSelection(action: PayloadAction<{ node: Node | null }>): Generator<any, void, any> {
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph) return;

  // Update graph visualization
  const cyElement = document.querySelector('.cytoscape-container');
  if (!cyElement) return;

  const cy = (cyElement as any).cy;
  if (!cy) return;

  // Clear all selected classes
  cy.$('node.selected').removeClass('selected');

  // Add selected class to current node
  if (action.payload.node) {
    const node = cy.$(`node[id="${action.payload.node.id}"]`);
    if (node.length > 0) {
      node.addClass('selected');
    }
  }
}

// Handle node creation
function* handleNodeCreation(action: PayloadAction<{ 
  graphId: string;
  label: string;
  position: { x: number; y: number };
  nodeId: string;
}>): Generator<any, void, any> {
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph || graph.id !== action.payload.graphId) return;

  // Get default color scheme
  const scheme = defaultColors.blue;

  // Update graph visualization
  const cyElement = document.querySelector('.cytoscape-container');
  if (!cyElement) return;

  const cy = (cyElement as any).cy;
  if (!cy) return;

  cy.add({
    group: 'nodes',
    data: { 
      id: action.payload.nodeId,
      label: action.payload.label,
      properties: {
        chatHistory: [],
        gradient: scheme.gradient,
        border: scheme.border,
        text: scheme.text,
        color: 'blue'
      }
    },
    position: action.payload.position
  });
}

// Handle node movement
function* handleNodeMovement(action: PayloadAction<{
  id: string;
  position: { x: number; y: number };
}>): Generator<any, void, any> {
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph) return;

  // Update graph visualization
  const cyElement = document.querySelector('.cytoscape-container');
  if (!cyElement) return;

  const cy = (cyElement as any).cy;
  if (!cy) return;

  const node = cy.$(`node[id="${action.payload.id}"]`);
  if (node.length > 0) {
    // Update Cytoscape visualization
    node.position(action.payload.position);
    
    // Persist the position update in Redux store
    yield put(updateNodePosition({
      nodeId: action.payload.id,
      position: action.payload.position
    }));
  }
}

// Handle node editing
function* handleNodeEdit(action: PayloadAction<{
  id: string;
  changes: Partial<Node>;
}>): Generator<any, void, any> {
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph) return;

  // Update graph visualization
  const cyElement = document.querySelector('.cytoscape-container');
  if (!cyElement) return;

  const cy = (cyElement as any).cy;
  if (!cy) return;

  const node = cy.$(`node[id="${action.payload.id}"]`);
  if (node.length > 0) {
    if (action.payload.changes.label) {
      node.data('label', action.payload.changes.label);
    }
    if (action.payload.changes.properties) {
      node.data('properties', {
        ...node.data('properties'),
        ...action.payload.changes.properties
      });
    }
  }
}

// Handle node connection
function* handleNodeConnection(action: PayloadAction<{
  source: string;
  target: string;
  label?: string;
}>): Generator<any, void, any> {
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph) return;

  // Update graph visualization
  const cyElement = document.querySelector('.cytoscape-container');
  if (!cyElement) return;

  const cy = (cyElement as any).cy;
  if (!cy) return;

  cy.add({
    group: 'edges',
    data: {
      id: `${action.payload.source}-${action.payload.target}`,
      source: action.payload.source,
      target: action.payload.target,
      label: action.payload.label
    }
  });
}

// Handle word node creation with edge
function* handleWordNodeCreationWithEdge(action: PayloadAction<{
  parentNodeId: string;
  word: string;
  position: { x: number; y: number };
  nodeId: string;
  graphId?: string;
}>): Generator<any, void, any> {
  console.log('handleWordNodeCreationWithEdge: Starting', action.payload);
  
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph) {
    console.warn('handleWordNodeCreationWithEdge: No current graph');
    return;
  }
  
  // Verify the graph ID matches if provided
  if (action.payload.graphId && action.payload.graphId !== graph.id) {
    console.warn('handleWordNodeCreationWithEdge: Graph ID mismatch', {
      payloadGraphId: action.payload.graphId,
      currentGraphId: graph.id
    });
    return;
  }

  console.log('handleWordNodeCreationWithEdge: Graph verified', {
    graphId: graph.id,
    nodeCount: graph.nodes.length,
    edgeCount: graph.edges.length
  });

  try {
    // Get default color scheme
    const scheme = defaultColors.blue;

    // Update graph state - visualization will be handled by React
    yield put(addNode({
      graphId: graph.id,
      node: {
        id: action.payload.nodeId,
        label: action.payload.word,
        position: action.payload.position,
        properties: {
          chatHistory: [],
          gradient: scheme.gradient,
          border: scheme.border,
          text: scheme.text,
          color: 'blue'
        }
      }
    }));

    console.log('handleWordNodeCreationWithEdge: Node added to state', {
      nodeId: action.payload.nodeId,
      graphId: graph.id
    });

    // Add edge to graph state
    yield put(addEdge({
      source: action.payload.parentNodeId,
      target: action.payload.nodeId,
      label: '',
      graphId: graph.id
    }));

    console.log('handleWordNodeCreationWithEdge: Edge added to state', {
      source: action.payload.parentNodeId,
      target: action.payload.nodeId,
      graphId: graph.id
    });

    // Short delay to ensure state is updated
    yield new Promise(resolve => setTimeout(resolve, 100));

    // Create the prompt with graph context
    const content = `You are a knowledgeable assistant. This is part of a knowledge graph titled "${graph.title}". Please provide a clear and concise definition of: ${action.payload.word}`;

    // Add user message
    yield put(addMessage({
      nodeId: action.payload.nodeId,
      role: 'user',
      content
    }));

    console.log('handleWordNodeCreationWithEdge: Added auto-prompt for definition', {
      nodeId: action.payload.nodeId,
      word: action.payload.word
    });

    // Start streaming state for definition request
    yield put({ type: 'chat/startStreaming', payload: { nodeId: action.payload.nodeId } });

    // Trigger OpenRouter query
    yield put({
      type: 'chat/sendMessage',
      payload: {
        nodeId: action.payload.nodeId,
        content
      }
    });

    console.log('handleWordNodeCreationWithEdge: Triggered OpenRouter query', {
      nodeId: action.payload.nodeId,
      content
    });

  } catch (error) {
    console.error('handleWordNodeCreationWithEdge: Error', error);
  }
}

// Handle graph load success
function* handleGraphLoadSuccess(action: PayloadAction<Graph>): Generator<any, void, any> {
  const graph: Graph | null = yield select(getCurrentGraph);
  if (!graph) return;

  // Find node to focus (lastFocusedNodeId or first node)
  let nodeToFocus: Node | null = null;
  
  if (graph.lastFocusedNodeId) {
    nodeToFocus = graph.nodes.find((n: Node) => n.id === graph.lastFocusedNodeId) || null;
  }
  
  if (!nodeToFocus && graph.nodes.length > 0) {
    nodeToFocus = graph.nodes[0];
  }

  if (nodeToFocus) {
    console.log('graphUpdateSaga: Focusing node on graph load', {
      nodeId: nodeToFocus.id,
      isLastFocused: nodeToFocus.id === graph.lastFocusedNodeId
    });
    
    // Select the node
    yield put({
      type: 'node/selectNode',
      payload: { node: nodeToFocus }
    });
  }
}

// Handle rehydration
function* handleRehydrate(action: any): Generator<any, void, any> {
  if (!action.payload || action.key !== 'kgraph' || !action.payload.currentGraph) return;
  
  const graph = action.payload.currentGraph;
  if (!graph.lastFocusedNodeId) return;
  
  const node = graph.nodes.find((n: Node) => n.id === graph.lastFocusedNodeId);
  if (!node) return;
  
  console.log('graphUpdateSaga: Restoring node selection on rehydrate', {
    nodeId: node.id,
    graphId: graph.id
  });
  
  yield put({
    type: 'node/selectNode',
    payload: { node }
  });
}

// Watch for node actions
export function* graphUpdateSaga(): Generator<any, void, any> {
  yield all([
    takeEvery('node/selectNode', handleNodeSelection),
    takeEvery('node/createNode', handleNodeCreation),
    takeEvery('node/moveNode', handleNodeMovement),
    takeEvery('node/editNode', handleNodeEdit),
    takeEvery('node/connectNodes', handleNodeConnection),
    takeEvery('node/createWordNode', handleWordNodeCreationWithEdge),
    takeEvery('graph/loadGraphSuccess', handleGraphLoadSuccess),
    takeEvery(REHYDRATE, handleRehydrate)
  ]);
}
