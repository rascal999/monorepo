import { takeEvery, select, put } from 'redux-saga/effects';
import { updateNodeChatHistory } from '../slices/nodeSlice';
import { updateNodeInGraph } from '../slices/graphSlice';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Graph, Node } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// Selector to get current graph
const getCurrentGraph = (state: { graph: { currentGraph: Graph | null } }) => state.graph.currentGraph;

// Handle chat message updates
function* handleChatMessage(action: PayloadAction<{
  nodeId: string;
  role: 'user' | 'assistant';
  content: string;
}>) {
  console.log('chatUpdateSaga: Handling chat message', action.payload);
  const graph: Graph | null = yield select(getCurrentGraph);
  console.log('chatUpdateSaga: Current graph', graph);
  if (!graph) return;

  const node = graph.nodes.find(n => n.id === action.payload.nodeId);
  console.log('chatUpdateSaga: Found node', node);
  if (!node) return;

  const message = {
    role: action.payload.role,
    content: action.payload.content
  };

  // Create updated node with new chat history
  const chatHistory = node.properties.chatHistory || [];
  const updatedNode = {
    ...node,
    properties: {
      ...node.properties,
      chatHistory: [...chatHistory, message]
    }
  };
  console.log('chatUpdateSaga: Updated node', updatedNode);

  // First ensure node is selected
  yield put({ 
    type: 'node/selectNode', 
    payload: { node: updatedNode }
  });

  // Then update both node and graph state
  console.log('chatUpdateSaga: Dispatching updateNodeChatHistory');
  yield put(updateNodeChatHistory({
    nodeId: action.payload.nodeId,
    message
  }));

  console.log('chatUpdateSaga: Dispatching updateNodeInGraph');
  yield put(updateNodeInGraph({
    nodeId: action.payload.nodeId,
    changes: updatedNode
  }));
}

// Watch for chat actions
export function* chatUpdateSaga() {
  yield takeEvery('chat/addMessage', handleChatMessage);
}
