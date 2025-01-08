import { useEffect, useRef } from 'react';
import { useGraphPersistence } from './useGraphPersistence';
import { useGraphOperations } from './useGraphOperations';
import { useGraphUpdate } from './useGraphUpdate';
import { useGraphClear } from './useGraphClear';
import { useGraphIO } from './useGraphIO';

export function useGraphState() {
  // Get persistence state
  const {
    graphs,
    setGraphs,
    activeGraph,
    setActiveGraph,
    clearData: clearPersistentData
  } = useGraphPersistence();

  // Track initialization
  const initializedRef = useRef(false);

  // Debug current state
  useEffect(() => {
    console.log('[GraphState] State updated:', {
      graphCount: graphs.length,
      activeGraphId: activeGraph?.id,
      activeNodeCount: activeGraph?.nodes?.length,
      isInitialized: initializedRef.current
    });

    // Mark as initialized once we have an active graph
    if (activeGraph && !initializedRef.current) {
      initializedRef.current = true;
      console.log('[GraphState] Initialized with graph:', activeGraph.id);
    }
  }, [graphs, activeGraph]);

  // Get operations with validation
  const operations = useGraphOperations(graphs, setGraphs, setActiveGraph);

  // Get throttled update function
  const updateGraph = useGraphUpdate(operations?.updateGraph);

  // Get clear functionality
  const clearData = useGraphClear(setGraphs, setActiveGraph, clearPersistentData);

  // Get import/export functionality
  const { exportGraph, importGraph } = useGraphIO(graphs, setGraphs, setActiveGraph);

  // Extract operations with validation
  const {
    createGraph = (title) => {
      console.error('[GraphState] createGraph not available');
      return null;
    },
    deleteGraph = (graphId) => {
      console.error('[GraphState] deleteGraph not available');
      return false;
    },
    setNodeLoading = (nodeId, isLoading) => {
      console.error('[GraphState] setNodeLoading not available');
    }
  } = operations || {};

  // Sync graph updates with initialization check
  useEffect(() => {
    if (!activeGraph) return;

    console.log('[GraphState] Syncing graph:', {
      id: activeGraph.id,
      nodeCount: activeGraph.nodes.length,
      dataCount: Object.keys(activeGraph.nodeData).length,
      isInitialized: initializedRef.current
    });

    // Only update graphs if initialized or this is initial graph
    if (initializedRef.current || graphs.length === 0) {
      setGraphs(prevGraphs => {
        const currentGraph = prevGraphs.find(g => g.id === activeGraph.id);
        if (!currentGraph) {
          console.log('[GraphState] Adding new graph');
          return [...prevGraphs, activeGraph];
        }
        if (JSON.stringify(currentGraph) !== JSON.stringify(activeGraph)) {
          console.log('[GraphState] Updating existing graph');
          return prevGraphs.map(g => g.id === activeGraph.id ? activeGraph : g);
        }
        return prevGraphs;
      });
    }
  }, [activeGraph, graphs.length, setGraphs]);

  // Prevent state reset on unmount
  useEffect(() => {
    return () => {
      console.log('[GraphState] Cleanup - preserving state');
    };
  }, []);

  return {
    graphs,
    activeGraph,
    setActiveGraph,
    createGraph,
    updateGraph,
    clearData,
    deleteGraph,
    setNodeLoading,
    exportGraph,
    importGraph
  };
}
