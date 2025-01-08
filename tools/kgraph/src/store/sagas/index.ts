import { all, call, put, select, takeLatest, delay } from 'redux-saga/effects';
import { ActionTypes, AppState, Graph } from '../types';
import { PayloadAction } from '@reduxjs/toolkit';
import { setError, clearError, clearLoading, loadGraphSuccess, restoreState } from '../slices/appSlice';

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
      // Dispatch actions to restore state
      // This will be handled by the reducers
      yield put(restoreState(parsed));
    }
  } catch (error) {
    yield put(setError('Failed to load from localStorage'));
  }
}

// Chat
function* handleSendMessage(action: PayloadAction<{ content: string }>): Generator {
  try {
    yield put(clearError());
    // TODO: Implement OpenRouter API integration
    const response = 'AI response placeholder';
    yield put({ 
      type: ActionTypes.RECEIVE_MESSAGE, 
      payload: { role: 'assistant', content: response }
    });
  } catch (error) {
    yield put(setError('Failed to send message'));
  }
}

// Graph Operations
function* handleLoadGraph(action: PayloadAction<string>): Generator {
  try {
    console.log('Saga: handleLoadGraph called with id:', action.payload);
    
    // Set loading state at the start
    yield put({ type: 'app/setLoading', payload: action.payload });
    
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
    // Validate graph data
    if (!data.nodes || !data.edges) {
      throw new Error('Invalid graph data');
    }
    // Import will be handled by reducer
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
    // Create download
    const dataStr = JSON.stringify(state.currentGraph);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    // Create and trigger download link
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
      takeLatest('app/loadGraph', function* (action: PayloadAction<string>) {
        console.log('loadGraph action caught in root saga:', action);
        yield call(handleLoadGraph, action);
      }),
      
      // Chat
      takeLatest(ActionTypes.SEND_MESSAGE, handleSendMessage),
      
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
      ], handleStateChange)
    ]);
    console.log('Root saga setup complete');
  } catch (error) {
    console.error('Error in root saga:', error);
  }
}
