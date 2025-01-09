import { all, call, put, select, takeLatest } from 'redux-saga/effects';
import { graphUpdateSaga } from './graphUpdateSaga';
import { chatUpdateSaga } from './chatUpdateSaga';
import { modelsSaga } from './modelsSaga';
import { PayloadAction } from '@reduxjs/toolkit';
import { loadGraphSuccess, restoreState, addNode } from '../slices/graphSlice';
import { addMessage } from '../slices/chatSlice';
import { setError, clearError, setLoading, clearLoading } from '../slices/uiSlice';
import type { Graph, Node } from '../types';

// Selectors
const getState = (state: { 
  graph: { graphs: Graph[]; currentGraph: Graph | null }; 
  node: { selectedNode: any }; 
  ui: { error: string | null; loading: any; selectedModel: string; theme: string }; 
}) => ({
  graphs: state.graph.graphs,
  currentGraph: state.graph.currentGraph,
  selectedNode: state.node.selectedNode,
  error: state.ui.error,
  loading: state.ui.loading,
  selectedModel: state.ui.selectedModel,
  theme: state.ui.theme
});

// Local Storage
function* saveToLocalStorage(): Generator {
  try {
    const state = yield select(getState);
    yield call([localStorage, 'setItem'], 'kgraph', JSON.stringify({
      graphs: state.graphs,
      currentGraph: state.currentGraph,
      ui: {
        selectedModel: state.selectedModel,
        theme: state.theme
      }
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
      // Restore graph state
      yield put(restoreState({
        graphs: parsed.graphs,
        currentGraph: parsed.currentGraph
      }));

      // Restore UI state if it exists
      if (parsed.ui) {
        if (parsed.ui.selectedModel) {
          yield put({ type: 'ui/setAIModel', payload: parsed.ui.selectedModel });
        }
        if (parsed.ui.theme) {
          yield put({ type: 'ui/setTheme', payload: parsed.ui.theme });
        }
      }

      // After state restoration, select appropriate node if there's a current graph
      if (parsed.currentGraph) {
        const nodeToSelect = parsed.currentGraph.nodes.find((n: Node) => 
          n.id === parsed.currentGraph.lastFocusedNodeId
        ) || parsed.currentGraph.nodes[0];

        if (nodeToSelect) {
          // Select the node
          yield put({ 
            type: 'node/selectNode', 
            payload: { node: nodeToSelect }
          });
          
        }
      }
    }
  } catch (error) {
    yield put(setError('Failed to load from localStorage'));
  }
}

// Handle graph creation with initial node
function* handleGraphCreation(action: PayloadAction<{ title: string; id: string }>): Generator {
  try {
    const { id: graphId, title } = action.payload;
    const nodeId = Date.now().toString();
    
    // Create initial node
    const node = {
      id: nodeId,
      label: title,
      position: { x: 0, y: 0 },
      properties: { chatHistory: [] }
    };
    
    // Add node to graph
    yield put(addNode({ graphId, node }));
    
    // Create initial chat message with graph context
    const content = `You are a knowledgeable assistant. This is part of a knowledge graph titled "${title}". Please provide a clear and concise definition (1-2 sentences) of: ${title}`;
    
    // Add user message
    yield put(addMessage({
      nodeId,
      role: 'user',
      content
    }));
    
    // Send to OpenRouter
    yield put({
      type: 'chat/sendMessage',
      payload: {
        nodeId,
        content
      }
    });
  } catch (error: any) {
    console.error('Error in handleGraphCreation:', error);
    yield put(setError(error.message || 'Failed to create graph'));
  }
}

// Chat
function* handleSendMessage(action: PayloadAction<{ nodeId: string; content: string }>): Generator {
  try {
    yield put(clearError());
    console.log('Sending message to OpenRouter:', action.payload.content);
    
    const apiState = yield select((state) => ({
      apiKey: import.meta.env.VITE_OPENROUTER_API_KEY,
      selectedModel: state.ui.selectedModel
    }));

    if (!apiState.apiKey) {
      throw new Error('OpenRouter API key not found. Please set VITE_OPENROUTER_API_KEY in .env');
    }

    // Get current graph and determine if this is not the first node
    const graphState = yield select(getState);
    const currentGraph = graphState.currentGraph;
    const isNotFirstNode = currentGraph && currentGraph.nodes[0].id !== action.payload.nodeId;
    
    // Construct context message
    const contextMessage = isNotFirstNode ? 
      `You are a knowledgeable assistant. This is part of a knowledge graph titled "${currentGraph?.title}". ` :
      'You are a knowledgeable assistant. ';

    console.log('Making API request to OpenRouter...');
    const response = yield call(fetch, 'https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiState.apiKey}`,
        'HTTP-Referer': window.location.origin,
        'X-Title': 'Knowledge Graph AI',
      },
      body: JSON.stringify({
        model: apiState.selectedModel,
        messages: [
          {
            role: 'system',
            content: contextMessage
          },
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

    yield put(addMessage({
      nodeId: action.payload.nodeId,
      role: 'assistant',
      content: aiResponse
    }));
  } catch (error: any) {
    console.error('Error in handleSendMessage:', error);
    yield put(setError(error.message || 'Failed to send message'));
  }
}

// Graph Operations
function* handleLoadGraph(action: PayloadAction<string>): Generator {
  try {
    console.log('Saga: handleLoadGraph called with id:', action.payload);
    
    yield put(setLoading(action.payload));
    
    const state = yield select(getState);
    console.log('Saga: Current state:', state);
    
    const graph = state.graphs.find((g: Graph) => g.id === action.payload);
    console.log('Saga: Found graph:', graph);
    
    if (graph) {
      console.log('Saga: Dispatching LOAD_GRAPH_SUCCESS');
      yield put(loadGraphSuccess(graph));

      // Select node based on lastFocusedNodeId or first node
      const nodeToSelect = graph.nodes.find((n: Node) => n.id === graph.lastFocusedNodeId) || graph.nodes[0];
      
      if (nodeToSelect) {
        console.log('Saga: Selecting node:', nodeToSelect.id);
        // Select the node
        yield put({ 
          type: 'node/selectNode', 
          payload: { node: nodeToSelect }
        });
        
      }
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
      takeLatest('graph/loadGraph', handleLoadGraph),
      
      // Graph Creation
      takeLatest('graph/createGraph', handleGraphCreation),
      
      // State Changes
      takeLatest([
        'graph/deleteGraph',
        'graph/clearAll',
        'graph/addNode',
        'graph/addEdge',
        'graph/updateGraphViewport',
        'graph/loadGraphSuccess',
        'node/editNode',
        'node/moveNode',
        'node/connectNodes',
        'node/deleteNode',
        'node/createWordNode',
        'ui/setAIModel',
        'ui/setTheme'
      ], handleStateChange),
      
      // Chat
      takeLatest('chat/sendMessage', handleSendMessage),
      
      // Graph and Chat Updates
      call(graphUpdateSaga),
      call(chatUpdateSaga),
      call(modelsSaga)
    ]);
    console.log('Root saga setup complete');
  } catch (error) {
    console.error('Error in root saga:', error);
  }
}
