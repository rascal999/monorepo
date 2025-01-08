import { assign } from 'xstate';
import { createContext } from './context';

export const actions = {
  clearSelection: assign({
    selectedNode: null
  }),
  
  clearError: assign({
    error: null
  }),
  
  initNodeData: assign((context, event) => ({
    selectedNode: {
      id: event.nodeId,
      data: event.data
    }
  })),
  
  setNodeData: assign((context, event) => ({
    selectedNode: {
      ...context.selectedNode,
      data: event.data
    }
  })),
  
  setError: assign({
    error: (_, event) => event.error
  }),
  
  saveToLocalStorage: ({ context }) => {
    try {
      localStorage.setItem('kgraph-state', JSON.stringify({
        viewport: context.viewport,
        graphs: context.graphs,
        currentGraph: context.currentGraph
      }));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  },
  
  loadFromLocalStorage: assign((context = createContext()) => {
    try {
      const saved = JSON.parse(localStorage.getItem('kgraph-state'));
      if (!saved) return context;
      return {
        ...context,
        viewport: saved.viewport || context.viewport,
        graphs: saved.graphs || context.graphs,
        currentGraph: saved.currentGraph || context.currentGraph
      };
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
      return context;
    }
  }),
  
  createAndSaveGraph: assign((context, event) => {
    console.log('createAndSaveGraph called with event:', event);
    const newGraph = {
      id: Date.now().toString(),
      title: event?.title || 'New Graph',
      nodes: [],
      edges: []
    };
    console.log('Created new graph:', newGraph);
    return {
      ...context,
      graphs: [...(context.graphs || []), newGraph],
      currentGraph: newGraph,
      error: null
    };
  }),

  clearNewGraph: assign({
    newGraph: null
  }),

  initChatSession: assign({
    chatSession: (_, event) => ({
      nodeId: event.nodeId,
      messages: []
    })
  }),
  
  processAIResponse: assign({
    chatSession: (context, event) => ({
      ...context.chatSession,
      messages: [...context.chatSession.messages, event.message]
    })
  })
};
