import { useState, useEffect } from 'react';

export function useGraphPersistence() {
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

  // Debug state changes
  useEffect(() => {
    console.log('[GraphPersistence] Graphs updated:', {
      count: graphs.length,
      ids: graphs.map(g => g.id)
    });
    localStorage.setItem('kgraph-graphs', JSON.stringify(graphs));
  }, [graphs]);

  useEffect(() => {
    console.log('[GraphPersistence] Active graph changed:', {
      id: activeGraph?.id,
      nodeCount: activeGraph?.nodes?.length,
      nodeDataCount: Object.keys(activeGraph?.nodeData || {}).length
    });

    if (activeGraph) {
      localStorage.setItem('kgraph-last-graph', activeGraph.id.toString());
      
      // Ensure active graph is in sync with graphs array
      setGraphs(prevGraphs => {
        const currentGraph = prevGraphs.find(g => g.id === activeGraph.id);
        if (currentGraph && JSON.stringify(currentGraph) !== JSON.stringify(activeGraph)) {
          console.log('[GraphPersistence] Syncing active graph with graphs array');
          return prevGraphs.map(g => g.id === activeGraph.id ? activeGraph : g);
        }
        return prevGraphs;
      });
    } else {
      localStorage.removeItem('kgraph-last-graph');
    }
  }, [activeGraph]);

  const clearData = () => {
    try {
      // Clear graph data
      localStorage.removeItem('kgraph-graphs');
      localStorage.removeItem('kgraph-last-graph');
      
      // Clear all viewport data for all graphs
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('kgraph-viewport-')) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  };

  return {
    graphs,
    setGraphs,
    activeGraph,
    setActiveGraph,
    clearData
  };
}
