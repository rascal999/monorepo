import { assign } from 'xstate';

export const states = {
  app_idle: {
    entry: { type: 'loadFromLocalStorage' },
    on: {
      CREATE_GRAPH: {
        target: 'graph_open',
        actions: [
          { type: 'clearError' },
          { type: 'createAndSaveGraph' },
          { type: 'saveToLocalStorage' }
        ]
      },
      OPEN_GRAPH: 'graph_open',
      DELETE_GRAPH: 'graph_deleting',
      CLEAR_ALL: 'clearing_data',
      OPEN_SETTINGS: 'settings_open'
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
};
