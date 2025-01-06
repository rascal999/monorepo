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
