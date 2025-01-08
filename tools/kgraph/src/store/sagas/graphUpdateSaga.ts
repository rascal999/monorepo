import { takeEvery, select, all, put, call } from 'redux-saga/effects';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Graph, Node } from '../types';
import { addNode, addEdge } from '../slices/graphSlice';
import cytoscape from 'cytoscape';

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

  // Update graph visualization
  const cyElement = document.querySelector('.cytoscape-container');
  if (!cyElement) return;

  const cy = (cyElement as any).cy;
  if (!cy) return;

  cy.add({
    group: 'nodes',
    data: { 
      id: action.payload.nodeId,
      label: action.payload.label
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
    node.position(action.payload.position);
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
  if (node.length > 0 && action.payload.changes.label) {
    node.data('label', action.payload.changes.label);
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

  // Wait for Cytoscape instance to be ready with timeout and retries
  const waitForCytoscape = () => new Promise<cytoscape.Core>((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 50; // 5 seconds total
    const interval = 100; // 100ms between attempts

    const checkCy = () => {
      const cyElement = document.querySelector('.cytoscape-container');
      if (!cyElement) {
        attempts++;
        if (attempts >= maxAttempts) {
          console.error('handleWordNodeCreationWithEdge: Timeout waiting for Cytoscape container', {
            attempts,
            maxAttempts,
            interval
          });
          reject(new Error('Timeout waiting for Cytoscape container'));
          return;
        }
        setTimeout(checkCy, interval);
        return;
      }

      // Try to get the Cytoscape instance
      const cy = (cyElement as any).cy;
      if (!cy) {
        attempts++;
        if (attempts >= maxAttempts) {
          console.error('handleWordNodeCreationWithEdge: Timeout waiting for Cytoscape instance', {
            attempts,
            maxAttempts,
            interval,
            hasContainer: Boolean(cyElement)
          });
          reject(new Error('Timeout waiting for Cytoscape instance'));
          return;
        }
        setTimeout(checkCy, interval);
        return;
      }

      console.log('handleWordNodeCreationWithEdge: Cytoscape ready', {
        nodes: cy.nodes().length,
        edges: cy.edges().length,
        attempts
      });
      resolve(cy);
    };

    // Start checking
    checkCy();
  });

  try {
    // First update the graph state
    yield put(addNode({
      graphId: graph.id,
      node: {
        id: action.payload.nodeId,
        label: action.payload.word,
        position: action.payload.position,
        properties: {
          chatHistory: []
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
      graphId: graph.id
    }));

    console.log('handleWordNodeCreationWithEdge: Edge added to state', {
      source: action.payload.parentNodeId,
      target: action.payload.nodeId,
      graphId: graph.id
    });

    // Now wait for Cytoscape and update visualization
    const cy: cytoscape.Core = yield call(waitForCytoscape);

    // Add the new node
    cy.add({
      group: 'nodes',
      data: {
        id: action.payload.nodeId,
        label: action.payload.word
      },
      position: action.payload.position
    });

    console.log('handleWordNodeCreationWithEdge: Node added to cytoscape', {
      nodeId: action.payload.nodeId,
      label: action.payload.word
    });

    // Create connection to parent node
    const edgeId = `${action.payload.parentNodeId}-${action.payload.nodeId}`;
    cy.add({
      group: 'edges',
      data: {
        id: edgeId,
        source: action.payload.parentNodeId,
        target: action.payload.nodeId
      }
    });

    console.log('handleWordNodeCreationWithEdge: Edge added to cytoscape', {
      edgeId,
      source: action.payload.parentNodeId,
      target: action.payload.nodeId
    });
  } catch (error) {
    console.error('handleWordNodeCreationWithEdge: Error', error);
  }
}

// Watch for node actions
export function* graphUpdateSaga(): Generator<any, void, any> {
  yield all([
    takeEvery('node/selectNode', handleNodeSelection),
    takeEvery('node/createNode', handleNodeCreation),
    takeEvery('node/moveNode', handleNodeMovement),
    takeEvery('node/editNode', handleNodeEdit),
    takeEvery('node/connectNodes', handleNodeConnection),
    takeEvery('node/createWordNode', handleWordNodeCreationWithEdge)
  ]);
}
