import { configureStore, Middleware } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import { persistStore, persistReducer, REHYDRATE } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import graphReducer, { rehydrateComplete } from './slices/graphSlice';
import type { Node } from './types';
import nodeReducer from './slices/nodeSlice';
import chatReducer from './slices/chatSlice';
import uiReducer from './slices/uiSlice';
import rootSaga from './sagas';

const graphPersistConfig = {
  key: 'kgraph',
  storage,
  whitelist: ['graphs', 'currentGraph'] // Persist graph-related state
};

const nodePersistConfig = {
  key: 'node',
  storage,
  whitelist: ['selectedNode'] // Persist selected node state
};

const persistedGraphReducer = persistReducer(graphPersistConfig, graphReducer);
const persistedNodeReducer = persistReducer(nodePersistConfig, nodeReducer);
const sagaMiddleware = createSagaMiddleware();

// Create rehydration middleware
const rehydrationMiddleware: Middleware = store => next => action => {
  if (action.type === REHYDRATE && action.key === 'kgraph') {
    console.log('REHYDRATE action received:', action);
    store.dispatch(rehydrateComplete(action.payload));

    // After rehydration, select appropriate node if there's a current graph
    if (action.payload?.currentGraph) {
      const { currentGraph } = action.payload;
      const nodeToSelect = currentGraph.nodes.find(
        (n: Node) => n.id === currentGraph.lastFocusedNodeId
      ) || currentGraph.nodes[0];

      if (nodeToSelect) {
        // Select the node
        store.dispatch({ 
          type: 'node/selectNode', 
          payload: { node: nodeToSelect }
        });
        
      }
    }
  }
  return next(action);
};

export const store = configureStore({
  reducer: {
    graph: persistedGraphReducer,
    node: persistedNodeReducer,
    chat: chatReducer,
    ui: uiReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE']
      }
    }).concat(sagaMiddleware, rehydrationMiddleware)
});

export const persistor = persistStore(store);

// Run sagas
sagaMiddleware.run(rootSaga);

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Export hooks
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
