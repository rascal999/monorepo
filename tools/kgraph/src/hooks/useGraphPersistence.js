import { useEffect } from 'react';

export function useGraphPersistence(graphs, activeGraph, viewport) {
  // Persist graphs to localStorage
  useEffect(() => {
    localStorage.setItem('kgraph-graphs', JSON.stringify(graphs));
  }, [graphs]);

  // Persist active graph ID
  useEffect(() => {
    if (activeGraph) {
      localStorage.setItem('kgraph-last-graph', activeGraph.id.toString());
    } else {
      localStorage.removeItem('kgraph-last-graph');
    }
  }, [activeGraph]);

  // Persist viewport state
  useEffect(() => {
    if (viewport) {
      localStorage.setItem('kgraph-viewport', JSON.stringify(viewport));
    }
  }, [viewport]);

  // Load initial state from localStorage
  const loadInitialState = () => {
    try {
      // Load graphs
      const savedGraphs = localStorage.getItem('kgraph-graphs');
      const graphs = savedGraphs ? JSON.parse(savedGraphs) : [];

      // Load active graph
      const lastGraphId = localStorage.getItem('kgraph-last-graph');
      const activeGraph = lastGraphId ? 
        graphs.find(g => g.id.toString() === lastGraphId) : 
        null;

      // Load viewport
      const savedViewport = localStorage.getItem('kgraph-viewport');
      const parsedViewport = savedViewport ? JSON.parse(savedViewport) : null;
      const viewport = validateViewport(parsedViewport) ? parsedViewport : getDefaultViewport();

      return { graphs, activeGraph, viewport };
    } catch (error) {
      console.error('Error loading state from localStorage:', error);
      return {
        graphs: [],
        activeGraph: null,
        viewport: getDefaultViewport()
      };
    }
  };

  return { loadInitialState };
}

function validateViewport(viewport) {
  return viewport && 
    Number.isFinite(viewport.x) && 
    Number.isFinite(viewport.y) && 
    Number.isFinite(viewport.zoom) &&
    !isNaN(viewport.x) && 
    !isNaN(viewport.y) && 
    !isNaN(viewport.zoom);
}

function getDefaultViewport() {
  return {
    x: 0,
    y: 0,
    zoom: 1
  };
}
