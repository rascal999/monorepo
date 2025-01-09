import { takeEvery, select, put, call } from 'redux-saga/effects';
import { updateNodeChatHistory } from '../slices/nodeSlice';
import { updateNodeInGraph } from '../slices/graphSlice';
import { startStreaming, appendStreamChunk, endStreaming, setStreamingError } from '../slices/chatSlice';
import { streamChatCompletion } from '../../services/openRouterApi';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Graph, Node } from '../types';
import { store } from '../index';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// Selector to get current graph
const getCurrentGraph = (state: { graph: { currentGraph: Graph | null } }) => state.graph.currentGraph;

// Handle streaming chat completion
function* handleChatCompletion(nodeId: string, messages: ChatMessage[]): Generator<any, void, any> {
  const selectedModel = yield select((state) => state.ui.selectedModel);
  if (!selectedModel) {
    yield put(setStreamingError('No model selected'));
    return;
  }

  yield put(startStreaming({ nodeId }));

  let streamContent = '';
  try {
    yield call(streamChatCompletion, 
      {
        model: selectedModel.id,
        messages,
        temperature: 0.7,
        max_tokens: 2000
      },
      (chunk: string) => {
        streamContent += chunk;
        // Only dispatch the chunk for UI feedback
        store.dispatch(appendStreamChunk({ nodeId, content: chunk }));
      },
      (error: Error) => {
        store.dispatch(setStreamingError(error.message));
      },
      () => {
        // Update chat history with complete message when streaming is done
        store.dispatch(updateNodeChatHistory({
          nodeId,
          message: {
            role: 'assistant',
            content: streamContent
          }
        }));
        store.dispatch(endStreaming());
      }
    );
  } catch (error) {
    yield put(setStreamingError(error instanceof Error ? error.message : 'Unknown error'));
  }
}

// Handle chat message
function* handleChatMessage(action: PayloadAction<{
  nodeId: string;
  role: 'user' | 'assistant';
  content: string;
}>): Generator<any, void, any> {
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

  // Update node in graph with new chat history
  const chatHistory = node.properties.chatHistory || [];
  console.log('chatUpdateSaga: Updating node with new chat history', {
    currentLength: chatHistory.length,
    newMessage: message
  });

  // Update both graph and node states
  const changes = {
    properties: {
      ...node.properties,
      chatHistory: [...chatHistory, message]
    }
  };

  // Update graph state
  yield put(updateNodeInGraph({
    nodeId: action.payload.nodeId,
    changes
  }));

  // Update node state
  yield put(updateNodeChatHistory({
    nodeId: action.payload.nodeId,
    message
  }));

  // If this is a user message, trigger AI response
  if (action.payload.role === 'user') {
    yield call(handleChatCompletion, action.payload.nodeId, [...chatHistory, message]);
  }
}

// Watch for chat actions
export function* chatUpdateSaga(): Generator<any, void, any> {
  yield takeEvery('chat/addMessage', handleChatMessage);
}
