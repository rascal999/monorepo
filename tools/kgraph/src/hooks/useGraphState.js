import { useEffect, useRef } from 'react';
import { useGraphPersistence } from './useGraphPersistence';
import { useViewportState } from './useViewportState';
import { useGraphOperations } from './useGraphOperations';

// Store handleGetDefinition callback
let globalHandleGetDefinition = null;

export function useGraphState() {
  const handleGetDefinitionRef = useRef(globalHandleGetDefinition);
  const {
    graphs,
    setGraphs,
    activeGraph,
    setActiveGraph,
    clearData: clearPersistentData
  } = useGraphPersistence();

  // Track current viewport state
  const {
    viewport,
    updateViewport
  } = useViewportState(activeGraph?.id);

  const {
    createGraph,
    updateGraph,
    deleteGraph,
    setNodeLoading
  } = useGraphOperations(setGraphs, setActiveGraph, handleGetDefinitionRef.current);

  // Update ref when global callback changes
  useEffect(() => {
    handleGetDefinitionRef.current = globalHandleGetDefinition;
  }, []);

  const clearData = () => {
    // Clear all viewport data
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('kgraph-viewport-')) {
        localStorage.removeItem(key);
      }
    });

    // Reset state
    clearPersistentData();
    setGraphs([]);
    setActiveGraph(null);

    // Reset global callback
    globalHandleGetDefinition = null;
    handleGetDefinitionRef.current = null;

    return null;
  };

  const result = {
    graphs,
    activeGraph,
    viewport,
    setActiveGraph,
    createGraph,
    updateGraph,
    updateViewport,
    clearData,
    deleteGraph,
    setNodeLoading
  };
  // Add static method to update the global callback
  useGraphState.setHandleGetDefinition = (callback) => {
    globalHandleGetDefinition = callback;
  };

  return result;
}
