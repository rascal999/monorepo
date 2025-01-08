import { configureStore, Middleware } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import { persistStore, persistReducer, REHYDRATE } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import appReducer, { rehydrateComplete } from './slices/appSlice';
import rootSaga from './sagas';

const persistConfig = {
  key: 'kgraph',
  storage,
  whitelist: ['graphs', 'viewport', 'currentGraph'] // Persist these parts of state
};

const persistedReducer = persistReducer(persistConfig, appReducer);
const sagaMiddleware = createSagaMiddleware();

// Create rehydration middleware
const rehydrationMiddleware: Middleware = store => next => action => {
  if (action.type === REHYDRATE && action.key === 'kgraph') {
    console.log('REHYDRATE action received:', action);
    store.dispatch(rehydrateComplete(action.payload));
  }
  return next(action);
};

export const store = configureStore({
  reducer: {
    app: persistedReducer
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
