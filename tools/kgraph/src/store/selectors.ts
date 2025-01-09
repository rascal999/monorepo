import { createSelector } from '@reduxjs/toolkit';
import type { RootState } from './index';
import type { Graph, Node, Viewport, Theme } from './types';
import type { UIState } from './slices/uiSlice';

export const selectSelectedNode = createSelector(
  [(state: RootState) => state.node.selectedNode],
  (selectedNode): Node | null => selectedNode
);

export const selectCurrentGraph = createSelector(
  [(state: RootState) => state.graph.currentGraph],
  (currentGraph): Graph | null => currentGraph
);

export const selectChatHistory = createSelector(
  [selectSelectedNode],
  (selectedNode) => selectedNode?.properties.chatHistory || []
);

export const selectStreaming = createSelector(
  [(state: RootState) => state.chat.streaming],
  (streaming) => streaming
);

export const selectChatScroll = createSelector(
  [(state: RootState) => state.ui.chatScroll],
  (chatScroll): UIState['chatScroll'] => chatScroll
);

const defaultViewport: Viewport = { zoom: 1, position: { x: 0, y: 0 } };

export const selectViewport = createSelector(
  [selectCurrentGraph],
  (currentGraph): Viewport => currentGraph?.viewport ?? defaultViewport
);

export const selectGraphs = createSelector(
  [(state: RootState) => state.graph.graphs],
  (graphs): Graph[] => graphs
);

export const selectSettingsOpen = createSelector(
  [(state: RootState) => state.ui.settingsOpen],
  (settingsOpen): boolean => settingsOpen
);

export const selectLoading = createSelector(
  [(state: RootState) => state.ui.loading],
  (loading): UIState['loading'] => loading
);

export const selectTheme = createSelector(
  [(state: RootState) => state.ui.theme],
  (theme): Theme => theme
);

export const selectSelectedModel = createSelector(
  [(state: RootState) => state.ui.selectedModel],
  (model): string => model
);

export const selectAIModels = createSelector(
  [(state: RootState) => state.ui.aiModels],
  (models): UIState['aiModels'] => models
);

export const selectModelSearchQuery = createSelector(
  [(state: RootState) => state.ui.modelSearchQuery],
  (query): string => query
);

export const selectSettingsTab = createSelector(
  [(state: RootState) => state.ui.settingsTab],
  (tab): UIState['settingsTab'] => tab
);

export const selectModelsLoading = createSelector(
  [(state: RootState) => state.ui.modelsLoading],
  (loading): boolean => loading
);

export const selectModelsError = createSelector(
  [(state: RootState) => state.ui.modelsError],
  (error): string | null => error
);

export const selectFilteredModels = createSelector(
  [selectAIModels, selectModelSearchQuery, selectSelectedModel],
  (models, query, selectedModel) => models
    .filter(model => 
      model.name.toLowerCase().includes(query.toLowerCase()) ||
      model.provider.toLowerCase().includes(query.toLowerCase())
    )
    .sort((a, b) => {
      if (a.id === selectedModel) return -1;
      if (b.id === selectedModel) return 1;
      return a.name.localeCompare(b.name);
    })
);
