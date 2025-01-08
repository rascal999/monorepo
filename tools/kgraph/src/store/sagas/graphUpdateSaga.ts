import { takeEvery, select, all } from 'redux-saga/effects';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Graph, Node } from '../types';

// Selector to get current graph
const getCurrentGraph = (state: { graph: { currentGraph: Graph | null } }) => state.graph.currentGraph;

// Handle node selection
function* handleNodeSelection(action: PayloadAction<{ node: Node | null }>) {
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
}>) {
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
}>) {
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
}>) {
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

// Watch for node actions
export function* graphUpdateSaga() {
  yield all([
    takeEvery('node/selectNode', handleNodeSelection),
    takeEvery('node/createNode', handleNodeCreation),
    takeEvery('node/moveNode', handleNodeMovement),
    takeEvery('node/editNode', handleNodeEdit)
  ]);
}
