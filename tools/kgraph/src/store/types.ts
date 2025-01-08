export interface Viewport {
  zoom: number;
  position: { x: number; y: number };
}

export interface Node {
  id: string;
  label: string;
  position: { x: number; y: number };
  properties: {
    chatHistory?: Array<{
      role: 'user' | 'assistant';
      content: string;
    }>;
    [key: string]: any;
  };
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
  viewport: Viewport;
  lastFocusedNodeId?: string;
}

export type Theme = 'light' | 'dark';

export interface AppState {
  graphs: Graph[];
  currentGraph: Graph | null;
  selectedNode: Node | null;
  draggingNodeId: string | null;
  error: string | null;
  theme: Theme;
  loading: {
    graphId: string | null;
    status: boolean;
  };
  panelWidth: number;
}

// Action Types
export enum ActionTypes {
  // App Actions
  LOAD_GRAPH = 'LOAD_GRAPH',
  LOAD_GRAPH_SUCCESS = 'LOAD_GRAPH_SUCCESS',
  CREATE_GRAPH = 'CREATE_GRAPH',
  DELETE_GRAPH = 'DELETE_GRAPH',
  CLEAR_ALL = 'CLEAR_ALL',
  OPEN_SETTINGS = 'OPEN_SETTINGS',
  
  // Node Actions
  CREATE_NODE = 'CREATE_NODE',
  SELECT_NODE = 'SELECT_NODE',
  EDIT_NODE = 'EDIT_NODE',
  MOVE_NODE = 'MOVE_NODE',
  START_DRAG = 'START_DRAG',
  END_DRAG = 'END_DRAG',
  CONNECT_NODE = 'CONNECT_NODE',
  DELETE_NODE = 'DELETE_NODE',
  DESELECT_NODE = 'DESELECT_NODE',
  
  // Chat Actions
  OPEN_CHAT = 'OPEN_CHAT',
  CLOSE_CHAT = 'CLOSE_CHAT',
  SEND_MESSAGE = 'SEND_MESSAGE',
  RECEIVE_MESSAGE = 'RECEIVE_MESSAGE',
  AUTO_PROMPT_NODE = 'AUTO_PROMPT_NODE',
  
  // Import/Export Actions
  IMPORT_GRAPH = 'IMPORT_GRAPH',
  EXPORT_GRAPH = 'EXPORT_GRAPH',
  
  // Error Actions
  SET_ERROR = 'SET_ERROR',
  CLEAR_ERROR = 'CLEAR_ERROR',
  
  // Theme Actions
  SET_THEME = 'SET_THEME',
  
  // Viewport Actions
  UPDATE_VIEWPORT = 'UPDATE_VIEWPORT',

  // Loading Actions
  SET_LOADING = 'SET_LOADING',
  CLEAR_LOADING = 'CLEAR_LOADING',

  // Panel Actions
  UPDATE_PANEL_WIDTH = 'UPDATE_PANEL_WIDTH'
}
