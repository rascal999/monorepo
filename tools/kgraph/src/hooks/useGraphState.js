import { useEffect, useRef } from 'react';
import { useGraphPersistence } from './useGraphPersistence';
import { useGraphOperations } from './useGraphOperations';
import { useGraphUpdate } from './useGraphUpdate';
import { useGraphClear } from './useGraphClear';
import { useGraphIO } from './useGraphIO';

export function useGraphState() {
  const {
    graphs,
    setGraphs,
    activeGraph,
    setActiveGraph,
    clearData: clearPersistentData
  } = useGraphPersistence();

  // Get operations with validation
  const operations = useGraphOperations(graphs, setGraphs, setActiveGraph);

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

  // Get throttled update function
  const updateGraph = useGraphUpdate(operations?.updateGraph);

  // Get clear functionality
  const clearData = useGraphClear(setGraphs, setActiveGraph, clearPersistentData);

  // Get import/export functionality
  const { exportGraph, importGraph } = useGraphIO(graphs, setGraphs, setActiveGraph);

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

  // Prevent unnecessary graph recreation
  useEffect(() => {
    if (activeGraph && graphs.length > 0) {
      const currentGraph = graphs.find(g => g.id === activeGraph.id);
      if (currentGraph && JSON.stringify(currentGraph) !== JSON.stringify(activeGraph)) {
        setGraphs(prevGraphs => 
          prevGraphs.map(g => g.id === activeGraph.id ? activeGraph : g)
        );
      }
    }
  }, [activeGraph, graphs]);

  const result = {
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

  return result;
}
