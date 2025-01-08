import { all, call, put, select, takeLatest, delay } from 'redux-saga/effects';
import { ActionTypes, AppState, Graph } from '../types';
import { PayloadAction } from '@reduxjs/toolkit';
import { setError, clearError, clearLoading, loadGraphSuccess, restoreState, addMessage, setLoading } from '../slices/appSlice';

// Selectors
const getState = (state: { app: AppState }) => state.app;

// Local Storage
function* saveToLocalStorage(): Generator {
  try {
    const state = yield select(getState);
    yield call([localStorage, 'setItem'], 'kgraph', JSON.stringify({
      graphs: state.graphs,
      viewport: state.viewport,
      currentGraph: state.currentGraph
    }));
  } catch (error) {
    yield put(setError('Failed to save to localStorage'));
  }
}

function* loadFromLocalStorage(): Generator {
  try {
    const data = yield call([localStorage, 'getItem'], 'kgraph');
    if (data) {
      const parsed = JSON.parse(data);
      yield put(restoreState(parsed));
    }
  } catch (error) {
    yield put(setError('Failed to load from localStorage'));
  }
}

// Chat
function* handleSendMessage(action: PayloadAction<{ nodeId: string; content: string }>): Generator {
  try {
    yield put(clearError());
    console.log('Sending message to OpenRouter:', action.payload.content);
    
    const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
    const model = import.meta.env.VITE_OPENROUTER_MODEL || 'mistralai/mistral-7b-instruct';

    if (!apiKey) {
      throw new Error('OpenRouter API key not found. Please set VITE_OPENROUTER_API_KEY in .env');
    }

    console.log('Making API request to OpenRouter...');
    const response = yield call(fetch, 'https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': window.location.origin,
        'X-Title': 'Knowledge Graph AI',
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: 'user',
            content: action.payload.content
          }
        ],
        temperature: 0.7,
        max_tokens: 150,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      })
    });

    if (!response.ok) {
      const error = yield response.json();
      console.error('OpenRouter API error:', error);
      console.error('Response status:', response.status);
      console.error('Response headers:', response.headers);
      throw new Error(`OpenRouter API error: ${error.message || 'Unknown error'} (${response.status})`);
    }

    const data = yield response.json();
    console.log('Received response from OpenRouter:', data);
    const aiResponse = data.choices[0]?.message?.content || 'No response from AI';

    yield put(addMessage({ nodeId: action.payload.nodeId, role: 'assistant', content: aiResponse }));
  } catch (error: any) {
    console.error('Error in handleSendMessage:', error);
    yield put(setError(error.message || 'Failed to send message'));
  }
}

// Handle node creation
function* handleNodeCreation(action: PayloadAction<{ label: string; position: { x: number; y: number } }>): Generator {
  try {
    console.log('Node creation detected:', action.payload.label);
    const state = yield select(getState);
    const currentNode = state.currentGraph?.nodes.find((n: any) => n.label === action.payload.label);
    if (currentNode) {
      const message = {
        nodeId: currentNode.id,
        role: 'user' as const,
        content: `You are a knowledgeable assistant. Please provide a clear and concise definition (1-2 sentences) of: ${action.payload.label}`
      };
      console.log('Adding message to chat:', message);
      yield put(addMessage(message));
      console.log('Dispatching message to OpenRouter:', message);
      yield put({ type: 'app/sendMessage', payload: message });
    }
  } catch (error: any) {
    console.error('Error in handleNodeCreation:', error);
    yield put(setError(error.message || 'Failed to process node creation'));
  }
}

// Graph Operations
function* handleLoadGraph(action: PayloadAction<string>): Generator {
  try {
    console.log('Saga: handleLoadGraph called with id:', action.payload);
    
    yield put(setLoading(action.payload));
    
    const state = yield select(getState);
    console.log('Saga: Current state:', state);
    
    const graph = state.graphs.find((g: any) => g.id === action.payload);
    console.log('Saga: Found graph:', graph);
    
    if (graph) {
      console.log('Saga: Dispatching LOAD_GRAPH_SUCCESS');
      yield put(loadGraphSuccess(graph));
    } else {
      console.log('Saga: Graph not found, dispatching error');
      yield put(setError('Graph not found'));
      yield put(clearLoading());
    }
  } catch (error) {
    console.error('Saga: Error in handleLoadGraph:', error);
    yield put(setError('Failed to load graph'));
    yield put(clearLoading());
  }
}

function* handleImportGraph(action: PayloadAction<{ data: Graph }>): Generator {
  try {
    yield put(clearError());
    const { data } = action.payload;
    if (!data.nodes || !data.edges) {
      throw new Error('Invalid graph data');
    }
    yield put({ type: 'IMPORT_GRAPH_SUCCESS', payload: data });
    yield call(saveToLocalStorage);
  } catch (error) {
    yield put(setError('Failed to import graph'));
  }
}

function* handleExportGraph(): Generator {
  try {
    yield put(clearError());
    const state = yield select(getState);
    if (!state.currentGraph) {
      throw new Error('No graph selected');
    }
    const dataStr = JSON.stringify(state.currentGraph);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const link = document.createElement('a');
    link.setAttribute('href', dataUri);
    link.setAttribute('download', `${state.currentGraph.title}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    yield put(setError('Failed to export graph'));
  }
}

// State Change Handlers
function* handleStateChange(): Generator {
  yield call(saveToLocalStorage);
}

// Root Saga
export default function* rootSaga(): Generator {
  try {
    console.log('Root saga started');
    yield all([
      // Initialize
      call(loadFromLocalStorage),
      
      // Graph Loading
      takeLatest('app/loadGraph', handleLoadGraph),
      
      // Graph Operations
      takeLatest(ActionTypes.IMPORT_GRAPH, handleImportGraph),
      takeLatest(ActionTypes.EXPORT_GRAPH, handleExportGraph),
      
      // State Changes
      takeLatest([
        ActionTypes.CREATE_GRAPH,
        ActionTypes.DELETE_GRAPH,
        ActionTypes.CLEAR_ALL,
        ActionTypes.CREATE_NODE,
        ActionTypes.EDIT_NODE,
        ActionTypes.MOVE_NODE,
        ActionTypes.CONNECT_NODE,
        ActionTypes.DELETE_NODE,
        ActionTypes.UPDATE_VIEWPORT,
        'app/loadGraphSuccess'
      ], handleStateChange),
      
      // Node Creation and Chat - Make sure these are handled before state changes
      takeLatest('app/createNode', function* (action: PayloadAction<{ label: string; position: { x: number; y: number } }>) {
        console.log('createNode action caught in root saga:', action);
        yield call(handleNodeCreation, action);
      }),
      takeLatest('app/sendMessage', function* (action: PayloadAction<{ nodeId: string; content: string }>) {
        console.log('sendMessage action caught in root saga:', action);
        yield call(handleSendMessage, action);
        console.log('sendMessage saga completed');
      })
    ]);
    console.log('Root saga setup complete');
  } catch (error) {
    console.error('Error in root saga:', error);
  }
}
