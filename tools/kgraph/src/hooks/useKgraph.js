import { useActor, useMachine } from '@xstate/react';
import { kgraphMachine } from '../machines/kgraphMachine';

// Selectors for different parts of the state
const selectViewport = (state) => state.context.viewport;
const selectGraphs = (state) => state.context.graphs;
const selectCurrentGraph = (state) => state.context.currentGraph;
const selectSelectedNode = (state) => state.context.selectedNode;
const selectError = (state) => state.context.error;
const selectChatSession = (state) => state.context.chatSession;

export const useKgraph = () => {
  const [state, send] = useMachine(kgraphMachine);

  // Use selectors to get specific parts of the state
  const viewport = selectViewport(state);
  const graphs = selectGraphs(state);
  const currentGraph = selectCurrentGraph(state);
  const selectedNode = selectSelectedNode(state);
  const error = selectError(state);
  const chatSession = selectChatSession(state);

  // Helper function to send events with error handling
  const sendEvent = (event) => {
    try {
      send(event);
    } catch (error) {
      console.error('Error sending event:', error);
      send({ type: 'ERROR', error: error.message });
    }
  };

  // Graph management
  const createGraph = (title) => {
    sendEvent({ type: 'CREATE_GRAPH', title });
    // Automatically save after creating
    sendEvent({ type: 'SAVE' });
  };
  const openGraph = (id) => sendEvent({ type: 'OPEN_GRAPH', id });
  const deleteGraph = (id) => sendEvent({ type: 'DELETE_GRAPH', id });
  const clearAllData = () => sendEvent({ type: 'CLEAR_ALL' });
  const openSettings = () => sendEvent({ type: 'OPEN_SETTINGS' });

  // Node management
  const createNode = (position) => sendEvent({ type: 'CREATE_NODE', position });
  const selectNode = (nodeId, data) => sendEvent({ type: 'SELECT_NODE', nodeId, data });
  const editNode = () => sendEvent({ type: 'EDIT' });
  const moveNode = () => sendEvent({ type: 'MOVE' });
  const connectNode = () => sendEvent({ type: 'CONNECT' });
  const deleteNode = () => sendEvent({ type: 'DELETE' });
  const deselectNode = () => sendEvent({ type: 'DESELECT' });

  // Position handling
  const setPosition = (position) => sendEvent({ type: 'POSITION_SET', position });

  // Chat functionality
  const startChat = () => sendEvent({ type: 'CHAT' });
  const sendMessage = (message) => sendEvent({ type: 'SEND_MESSAGE', message });
  const closeChat = () => sendEvent({ type: 'CLOSE' });

  // Import/Export
  const importGraph = (data) => sendEvent({ type: 'IMPORT', data });
  const exportGraph = () => sendEvent({ type: 'EXPORT' });

  // Error handling
  const retryAfterError = () => sendEvent({ type: 'RETRY' });
  const clearError = () => sendEvent({ type: 'CLEAR' });

  return {
    // State
    viewport,
    graphs,
    currentGraph,
    selectedNode,
    error,
    chatSession,
    
    // Graph management
    createGraph,
    openGraph,
    deleteGraph,
    clearAllData,
    openSettings,
    
    // Node management
    createNode,
    selectNode,
    editNode,
    moveNode,
    connectNode,
    deleteNode,
    deselectNode,
    
    // Position handling
    setPosition,
    
    // Chat functionality
    startChat,
    sendMessage,
    closeChat,
    
    // Import/Export
    importGraph,
    exportGraph,
    
    // Error handling
    retryAfterError,
    clearError,
    
    // Current state
    state
  };
};
