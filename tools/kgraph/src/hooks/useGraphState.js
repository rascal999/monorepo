import { useEffect, useRef, useCallback, useMemo, useState } from 'react';
import { useGraphPersistence } from './useGraphPersistence';
import { useGraphOperations } from './useGraphOperations';
import { useGraphValidation } from './useGraphValidation';

// Store handleGetDefinition callback
let globalHandleGetDefinition = null;

export function useGraphState() {
  const { validateGraph } = useGraphValidation();
  const handleGetDefinitionRef = useRef(globalHandleGetDefinition);
  const {
    graphs,
    setGraphs,
    activeGraph,
    setActiveGraph,
    clearData: clearPersistentData
  } = useGraphPersistence();

  // Get operations with validation
  const operations = useGraphOperations(graphs, setGraphs, setActiveGraph, handleGetDefinitionRef.current);

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

  // Track updates
  const updateTimeoutRef = useRef(null);
  const lastUpdateRef = useRef(null);
  const UPDATE_THROTTLE = 16; // ~60fps

  // Throttled update function
  const updateGraph = useCallback((...args) => {
    const now = Date.now();
    const timeSinceLastUpdate = now - (lastUpdateRef.current || 0);

    // Clear any pending update
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // If we're updating too frequently, throttle
    if (timeSinceLastUpdate < UPDATE_THROTTLE) {
      updateTimeoutRef.current = setTimeout(() => {
        if (operations?.updateGraph) {
          operations.updateGraph(...args);
          lastUpdateRef.current = Date.now();
        }
      }, UPDATE_THROTTLE - timeSinceLastUpdate);
      return;
    }

    // Otherwise update immediately
    if (operations?.updateGraph) {
      operations.updateGraph(...args);
      lastUpdateRef.current = now;
    }
  }, [operations]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, []);

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
    if (globalHandleGetDefinition) {
      handleGetDefinitionRef.current = globalHandleGetDefinition;
    }
  }, [globalHandleGetDefinition]);

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

  // Export/Import operations
  const exportGraph = (graphId) => {
    console.log('[GraphState] Exporting graph', graphId);
    
    // Find the graph to export
    const graph = graphs.find(g => g.id === graphId);
    if (!graph) {
      console.error('[GraphState] Graph not found for export:', graphId);
      return null;
    }

    // Get viewport data
    const viewportData = localStorage.getItem(`kgraph-viewport-${graphId}`);
    const viewport = viewportData ? JSON.parse(viewportData) : null;

    // Create export data structure
    const exportData = {
      version: '1.0',
      graph,
      viewport,
      exportDate: new Date().toISOString()
    };

    // Create and download file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    // Get initial node's label for filename
    const initialNode = graph.nodes[0];
    if (!initialNode?.data?.label) {
      console.error('[GraphState] Initial node label not found');
      return null;
    }
    const safeTitle = initialNode.data.label.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with single dash
      .replace(/^-+|-+$/g, ''); // Remove leading/trailing dashes
    a.download = `kgraph-${safeTitle}-${exportData.exportDate.split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const importGraph = async (file) => {
    console.log('[GraphState] Importing graph from file');
    
    try {
      const text = await file.text();
      const importData = JSON.parse(text);
      
      // Validate import data structure
      if (!importData.version || !importData.graph) {
        throw new Error('Invalid import data structure');
      }

      const graph = importData.graph;
      
      // Validate graph structure
      if (!validateGraph(graph)) {
        throw new Error('Invalid graph structure in import data');
      }
      
      // Generate new IDs to avoid conflicts
      const newGraphId = Date.now().toString();
      const idMap = new Map();
      
      // Update graph ID and node IDs
      const updatedGraph = {
        ...graph,
        id: parseInt(newGraphId),
        nodes: graph.nodes.map(node => {
          const newId = (Date.now() + Math.random() * 1000).toString();
          idMap.set(node.id, newId);
          return { ...node, id: newId };
        }),
        edges: graph.edges.map(edge => ({
          ...edge,
          id: (Date.now() + Math.random() * 1000).toString(),
          source: idMap.get(edge.source),
          target: idMap.get(edge.target)
        })),
        nodeData: Object.entries(graph.nodeData).reduce((acc, [oldId, data]) => {
          acc[idMap.get(oldId)] = data;
          return acc;
        }, {})
      };

      // Store viewport data if present
      if (importData.viewport) {
        localStorage.setItem(
          `kgraph-viewport-${newGraphId}`,
          JSON.stringify(importData.viewport)
        );
      }

      // Add graph to state
      setGraphs(prevGraphs => [...prevGraphs, updatedGraph]);
      setActiveGraph(updatedGraph);

      return updatedGraph;
    } catch (error) {
      console.error('[GraphState] Import failed:', error);
      throw new Error(`Import failed: ${error.message}`);
    }
  };

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
  // Add static method to update the global callback
  useGraphState.setHandleGetDefinition = (callback) => {
    globalHandleGetDefinition = callback;
  };

  return result;
}
