import { useEffect, useRef } from 'react';
import { useGraphPersistence } from './useGraphPersistence';
import { useViewportState } from './useViewportState';
import { useGraphOperations } from './useGraphOperations';
import { isValidViewport } from '../utils/viewport';

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
    updateViewport,
    loadSavedViewport
  } = useViewportState(activeGraph?.id);

  // Load saved viewport when switching graphs
  useEffect(() => {
    if (!activeGraph) return;

    // Try to load saved viewport from localStorage
    const saved = localStorage.getItem(`kgraph-viewport-${activeGraph.id}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (isValidViewport(parsed)) {
          console.log('[GraphState] Loading saved viewport for graph:', {
            graphId: activeGraph.id,
            viewport: parsed
          });
          updateViewport(parsed);
        }
      } catch (e) {
        console.error('[GraphState] Error loading viewport:', e);
      }
    }
  }, [activeGraph?.id]);

  // Get operations with validation
  const operations = useGraphOperations(setGraphs, setActiveGraph, handleGetDefinitionRef.current);

  // Validate operations
  useEffect(() => {
    if (!operations || typeof operations.updateGraph !== 'function') {
      console.error('[GraphState] Invalid operations:', {
        hasOperations: !!operations,
        updateGraphType: typeof operations?.updateGraph,
        availableOperations: operations ? Object.keys(operations) : []
      });
    }
  }, [operations]);

  // Wrap updateGraph to ensure it's always a function
  const updateGraph = (...args) => {
    console.log('[GraphState] updateGraph called with:', {
      args,
      hasOperations: !!operations,
      hasUpdateGraph: typeof operations?.updateGraph === 'function'
    });
    
    if (operations?.updateGraph) {
      return operations.updateGraph(...args);
    } else {
      console.error('[GraphState] updateGraph called but not available');
    }
  };

  const {
    createGraph = () => {
      console.error('[GraphState] createGraph called but not available');
    },
    deleteGraph = () => {
      console.error('[GraphState] deleteGraph called but not available');
    },
    setNodeLoading = () => {
      console.error('[GraphState] setNodeLoading called but not available');
    }
  } = operations || {};

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
