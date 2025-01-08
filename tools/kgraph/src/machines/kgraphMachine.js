import { createMachine, assign } from 'xstate';

const createContext = () => ({
  viewport: { zoom: 1, position: { x: 0, y: 0 } },
  graphs: [],
  currentGraph: null,
  selectedNode: null,
  error: null,
  chatSession: null,
  newGraph: null
});

export const kgraphMachine = createMachine({
  id: 'kgraph',
  context: createContext(),
  initial: 'app_idle',
  
  states: {
    app_idle: {
      entry: { type: 'loadFromLocalStorage' },
      on: {
        CREATE_GRAPH: 'graph_creating',
        OPEN_GRAPH: 'graph_open',
        DELETE_GRAPH: 'graph_deleting',
        CLEAR_ALL: 'clearing_data',
        OPEN_SETTINGS: 'settings_open'
      }
    },
    
    graph_creating: {
      entry: [
        { type: 'clearError' },
        { type: 'initNewGraph' }
      ],
      on: {
        SAVE: {
          target: 'graph_open',
          actions: [
            { type: 'saveNewGraph' },
            { type: 'saveToLocalStorage' }
          ]
        },
        CANCEL: {
          target: 'app_idle',
          actions: { type: 'clearNewGraph' }
        },
        ERROR: 'error'
      }
    },
    
    graph_open: {
      initial: 'node_idle',
      states: {
        node_idle: {
          entry: [
            { type: 'clearSelection' },
            { type: 'clearError' }
          ],
          on: {
            CREATE_NODE: 'node_creating',
            SELECT_NODE: 'node_selected',
            IMPORT: '#kgraph.importing',
            EXPORT: '#kgraph.exporting',
            CLOSE_GRAPH: '#kgraph.app_idle'
          }
        },
        
        node_creating: {
          on: {
            POSITION_SET: [{
              target: 'creating_node',
              guard: 'isValidPosition'
            }, {
              target: '#kgraph.error'
            }],
            CANCEL: 'node_idle',
            ERROR: '#kgraph.error'
          }
        },
        
        creating_node: {
          entry: { type: 'initNodeData' },
          exit: { type: 'saveToLocalStorage' },
          on: {
            SUCCESS: 'node_idle',
            ERROR: '#kgraph.error'
          }
        },
        
        node_selected: {
          entry: { type: 'initNodeData' },
          on: {
            EDIT: 'node_editing',
            MOVE: 'node_moving',
            CONNECT: 'node_connecting',
            DELETE: 'node_deleting',
            CHAT: 'chat_active',
            DESELECT: 'node_idle',
            ERROR: '#kgraph.error'
          }
        },
        
        node_editing: {
          on: {
            SAVE: {
              target: 'node_selected',
              actions: [
                { type: 'setNodeData' },
                { type: 'saveToLocalStorage' }
              ]
            },
            CANCEL: 'node_selected',
            ERROR: '#kgraph.error'
          }
        },
        
        node_moving: {
          on: {
            POSITION_SET: [{
              target: 'node_selected',
              guard: 'isValidPosition',
              actions: { type: 'saveToLocalStorage' }
            }, {
              target: '#kgraph.error'
            }],
            CANCEL: 'node_selected',
            ERROR: '#kgraph.error'
          }
        },
        
        node_connecting: {
          on: {
            TARGET_SELECTED: {
              target: 'node_selected',
              actions: { type: 'saveToLocalStorage' }
            },
            CANCEL: 'node_selected',
            ERROR: '#kgraph.error'
          }
        },
        
        node_deleting: {
          on: {
            CONFIRM: {
              target: 'node_idle',
              actions: { type: 'saveToLocalStorage' }
            },
            CANCEL: 'node_selected',
            ERROR: '#kgraph.error'
          }
        },
        
        chat_active: {
          entry: { type: 'initChatSession' },
          on: {
            SEND_MESSAGE: 'chat_processing',
            CLOSE: 'node_selected',
            ERROR: '#kgraph.error'
          }
        },
        
        chat_processing: {
          on: {
            MESSAGE_RECEIVED: {
              target: 'chat_active',
              actions: { type: 'processAIResponse' }
            },
            ERROR: '#kgraph.error'
          }
        }
      }
    },
    
    importing: {
      on: {
        SUCCESS: {
          target: 'graph_open',
          guard: 'isValidGraphData',
          actions: { type: 'saveToLocalStorage' }
        },
        ERROR: 'error'
      }
    },
    
    exporting: {
      on: {
        SUCCESS: 'graph_open',
        ERROR: 'error'
      }
    },
    
    graph_deleting: {
      on: {
        CONFIRM: {
          target: 'app_idle',
          actions: { type: 'saveToLocalStorage' }
        },
        CANCEL: 'app_idle',
        ERROR: 'error'
      }
    },
    
    clearing_data: {
      on: {
        CONFIRM: {
          target: 'app_idle',
          actions: { type: 'saveToLocalStorage' }
        },
        CANCEL: 'app_idle',
        ERROR: 'error'
      }
    },
    
    settings_open: {
      on: {
        SAVE: {
          target: 'app_idle',
          actions: { type: 'saveToLocalStorage' }
        },
        CANCEL: 'app_idle',
        ERROR: 'error'
      }
    },
    
    error: {
      entry: { type: 'setError' },
      on: {
        RETRY: {
          target: 'app_idle',
          actions: { type: 'clearError' }
        },
        CLEAR: {
          target: 'app_idle',
          actions: { type: 'clearError' }
        }
      }
    }
  }
}, {
  actions: {
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
    
    loadFromLocalStorage: assign(() => {
      try {
        const saved = JSON.parse(localStorage.getItem('kgraph-state'));
        return {
          viewport: saved?.viewport || { zoom: 1, position: { x: 0, y: 0 } },
          graphs: saved?.graphs || [],
          currentGraph: saved?.currentGraph || null,
          selectedNode: null,
          error: null
        };
      } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return createContext();
      }
    }),
    
    initNewGraph: assign({
      newGraph: (_, event) => ({
        id: Date.now().toString(),
        title: event.title || 'New Graph',
        nodes: [],
        edges: []
      })
    }),

    saveNewGraph: assign({
      graphs: (context) => [...context.graphs, context.newGraph],
      currentGraph: (context) => context.newGraph,
      newGraph: null
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
  },
  
  guards: {
    isValidPosition: (_, event) => {
      const { x, y } = event.position;
      return typeof x === 'number' && 
             typeof y === 'number' && 
             !isNaN(x) && 
             !isNaN(y);
    },
    
    isValidGraphData: (_, event) => {
      try {
        const data = event.data;
        return data && 
               Array.isArray(data.nodes) && 
               Array.isArray(data.edges);
      } catch {
        return false;
      }
    }
  }
});
