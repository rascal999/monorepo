import { all, call, put, select, takeLatest } from 'redux-saga/effects';
import { ActionTypes } from '../types';
import { setError, clearError } from '../slices/appSlice';

// Selectors
const getState = (state: any) => state.app;

// Local Storage
function* saveToLocalStorage() {
  try {
    const state = yield select(getState);
    yield call([localStorage, 'setItem'], 'kgraph', JSON.stringify({
      graphs: state.graphs,
      viewport: state.viewport
    }));
  } catch (error) {
    yield put(setError('Failed to save to localStorage'));
  }
}

function* loadFromLocalStorage() {
  try {
    const data = yield call([localStorage, 'getItem'], 'kgraph');
    if (data) {
      const parsed = JSON.parse(data);
      // Dispatch actions to restore state
      // This will be handled by the reducers
      yield put({ type: 'RESTORE_STATE', payload: parsed });
    }
  } catch (error) {
    yield put(setError('Failed to load from localStorage'));
  }
}

// Chat
function* handleSendMessage(action: any) {
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
function* handleImportGraph(action: any) {
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

function* handleExportGraph() {
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
function* handleStateChange() {
  yield call(saveToLocalStorage);
}

// Root Saga
export default function* rootSaga() {
  yield all([
    // Initialize
    call(loadFromLocalStorage),
    
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
      ActionTypes.UPDATE_VIEWPORT
    ], handleStateChange)
  ]);
}
