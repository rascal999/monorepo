import { useState, useEffect } from 'react';
import { useGraphValidation } from './useGraphValidation';

export function useGraphState() {
  // Initialize state
  const [graphs, setGraphs] = useState(() => {
    try {
      const saved = localStorage.getItem('kgraph-graphs');
      if (!saved) return [];
      
      const parsed = JSON.parse(saved);
      if (!Array.isArray(parsed)) {
        console.error('Invalid graphs data in localStorage');
        return [];
      }
      
      return parsed;
    } catch (error) {
      console.error('Error loading graphs from localStorage:', error);
      localStorage.removeItem('kgraph-graphs');
      return [];
    }
  });

  const [activeGraph, setActiveGraph] = useState(() => {
    try {
      const lastGraphId = localStorage.getItem('kgraph-last-graph');
      if (!lastGraphId) return null;

      const saved = localStorage.getItem('kgraph-graphs');
      if (!saved) return null;

      const graphs = JSON.parse(saved);
      if (!Array.isArray(graphs)) {
        console.error('Invalid graphs data in localStorage');
        return null;
      }

      const graph = graphs.find(g => g.id.toString() === lastGraphId);
      if (!graph) {
        console.error('Active graph not found in graphs array');
        localStorage.removeItem('kgraph-last-graph');
        return null;
      }

      return graph;
    } catch (error) {
      console.error('Error loading active graph from localStorage:', error);
      localStorage.removeItem('kgraph-last-graph');
      return null;
    }
  });

  // Setup persistence
  useEffect(() => {
    localStorage.setItem('kgraph-graphs', JSON.stringify(graphs));
  }, [graphs]);

  useEffect(() => {
    if (activeGraph) {
      localStorage.setItem('kgraph-last-graph', activeGraph.id.toString());
    } else {
      localStorage.removeItem('kgraph-last-graph');
    }
  }, [activeGraph]);
  
  // Initialize viewport state
  const [viewport, setViewport] = useState(() => {
    try {
      const saved = localStorage.getItem('kgraph-viewport');
      const parsed = saved ? JSON.parse(saved) : null;
      if (parsed && 
          Number.isFinite(parsed.x) && 
          Number.isFinite(parsed.y) && 
          Number.isFinite(parsed.zoom) &&
          !isNaN(parsed.x) && 
          !isNaN(parsed.y) && 
          !isNaN(parsed.zoom)) {
        return parsed;
      }
    } catch (e) {
      console.error('Error parsing viewport:', e);
    }
    return { x: 0, y: 0, zoom: 1 };
  });

  // Persist viewport
  useEffect(() => {
    if (viewport) {
      localStorage.setItem('kgraph-viewport', JSON.stringify(viewport));
    }
  }, [viewport]);

  const updateViewport = (newViewport) => {
    if (newViewport && 
        Number.isFinite(newViewport.x) && 
        Number.isFinite(newViewport.y) && 
        Number.isFinite(newViewport.zoom) &&
        !isNaN(newViewport.x) && 
        !isNaN(newViewport.y) && 
        !isNaN(newViewport.zoom)) {
      setViewport(newViewport);
    }
  };

  const resetViewport = () => {
    setViewport({ x: 0, y: 0, zoom: 1 });
  };

  // Initialize validation
  const {
    validateGraph,
    validateNodeData,
    validateGraphUpdate
  } = useGraphValidation();

  const createGraph = (title) => {
    const timestamp = Date.now().toString();
    const newGraph = {
      id: parseInt(timestamp),
      title,
      nodes: [{
        id: timestamp,
        type: 'default',
        position: { x: 250, y: 100 },
        data: { label: title }
      }],
      edges: [],
      nodeData: {
        [timestamp]: {
          chat: null,
          notes: '',
          quiz: []
        }
      },
      lastSelectedNodeId: timestamp
    };

    if (!validateGraph(newGraph)) {
      console.error('Invalid graph structure in createGraph');
      return;
    }

    setGraphs(prevGraphs => [...prevGraphs, newGraph]);
    setActiveGraph(newGraph);
  };

  const updateGraph = (updatedGraph, selectedNodeId = null) => {
    setGraphs(prevGraphs => {
      const currentGraph = prevGraphs.find(g => g.id === updatedGraph.id);
      if (!currentGraph) return prevGraphs;

      // Validate the update
      if (!validateGraphUpdate(updatedGraph, currentGraph)) {
        console.error('Invalid graph update');
        return prevGraphs;
      }

      // Handle node data updates
      const mergedNodeData = { ...currentGraph.nodeData };
      
      // First, handle any explicit nodeData updates
      if (updatedGraph.nodeData) {
        Object.assign(mergedNodeData, updatedGraph.nodeData);
      }
      
      // Then ensure all nodes have nodeData
      updatedGraph.nodes.forEach(node => {
        if (!mergedNodeData[node.id]) {
          mergedNodeData[node.id] = {
            chat: null,
            notes: '',
            quiz: []
          };
        }
      });

      // Remove nodeData for nodes that no longer exist
      const validNodeIds = new Set(updatedGraph.nodes.map(n => n.id));
      Object.keys(mergedNodeData).forEach(nodeId => {
        if (!validNodeIds.has(nodeId)) {
          delete mergedNodeData[nodeId];
        }
      });

      // Create the final graph update, preserving existing selection
      const graphToUpdate = {
        ...updatedGraph,
        lastSelectedNodeId: currentGraph.lastSelectedNodeId, // Always preserve existing selection
        nodeData: mergedNodeData
      };

      // Update graphs array
      return prevGraphs.map(g => 
        g.id === graphToUpdate.id ? graphToUpdate : g
      );
    });

    // Update active graph to match
    setActiveGraph(prevGraph => {
      if (prevGraph?.id !== updatedGraph.id) return prevGraph;
      
      return {
        ...updatedGraph,
        lastSelectedNodeId: prevGraph.lastSelectedNodeId, // Always preserve existing selection
        nodeData: {
          ...prevGraph.nodeData,
          ...updatedGraph.nodeData
        }
      };
    });
  };

  const clearData = () => {
    // Clear all state
    setGraphs([]);
    setActiveGraph(null);
    resetViewport();

    // Clear localStorage
    try {
      localStorage.removeItem('kgraph-graphs');
      localStorage.removeItem('kgraph-last-graph');
      localStorage.removeItem('kgraph-viewport');
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }

    return null;
  };

  return {
    graphs,
    activeGraph,
    viewport,
    setActiveGraph,
    createGraph,
    updateGraph,
    updateViewport,
    clearData
  };
}
