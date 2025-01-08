export interface Viewport {
  zoom: number;
  position: { x: number; y: number };
}

export interface Node {
  id: string;
  label: string;
  position: { x: number; y: number };
  properties: Record<string, any>;
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface Graph {
  id: string;
  title: string;
  nodes: Node[];
  edges: Edge[];
}

export interface AppState {
  viewport: Viewport;
  graphs: Graph[];
  currentGraph: Graph | null;
  selectedNode: Node | null;
  error: string | null;
  chatSession: {
    isActive: boolean;
    messages: Array<{
      role: 'user' | 'assistant';
      content: string;
    }>;
  };
}

// Action Types
export enum ActionTypes {
  // App Actions
  OPEN_GRAPH = 'OPEN_GRAPH',
  CREATE_GRAPH = 'CREATE_GRAPH',
  DELETE_GRAPH = 'DELETE_GRAPH',
  CLEAR_ALL = 'CLEAR_ALL',
  OPEN_SETTINGS = 'OPEN_SETTINGS',
  
  // Node Actions
  CREATE_NODE = 'CREATE_NODE',
  SELECT_NODE = 'SELECT_NODE',
  EDIT_NODE = 'EDIT_NODE',
  MOVE_NODE = 'MOVE_NODE',
  CONNECT_NODE = 'CONNECT_NODE',
  DELETE_NODE = 'DELETE_NODE',
  DESELECT_NODE = 'DESELECT_NODE',
  
  // Chat Actions
  OPEN_CHAT = 'OPEN_CHAT',
  CLOSE_CHAT = 'CLOSE_CHAT',
  SEND_MESSAGE = 'SEND_MESSAGE',
  RECEIVE_MESSAGE = 'RECEIVE_MESSAGE',
  
  // Import/Export Actions
  IMPORT_GRAPH = 'IMPORT_GRAPH',
  EXPORT_GRAPH = 'EXPORT_GRAPH',
  
  // Error Actions
  SET_ERROR = 'SET_ERROR',
  CLEAR_ERROR = 'CLEAR_ERROR',
  
  // Viewport Actions
  UPDATE_VIEWPORT = 'UPDATE_VIEWPORT'
}
