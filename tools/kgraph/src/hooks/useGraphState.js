import { useState, useEffect } from 'react';

export function useGraphState() {
  const [graphs, setGraphs] = useState(() => {
    const saved = localStorage.getItem('kgraph-graphs');
    return saved ? JSON.parse(saved) : [];
  });

  const [activeGraph, setActiveGraph] = useState(() => {
    const lastGraphId = localStorage.getItem('kgraph-last-graph');
    if (lastGraphId) {
      const saved = localStorage.getItem('kgraph-graphs');
      const graphs = saved ? JSON.parse(saved) : [];
      return graphs.find(g => g.id.toString() === lastGraphId);
    }
    return null;
  });

  const [viewport, setViewport] = useState(() => {
    try {
      const saved = localStorage.getItem('kgraph-viewport');
      const parsed = saved ? JSON.parse(saved) : null;
      // Validate viewport values
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
    // Return default viewport if saved state is invalid
    return {
      x: 0,
      y: 0,
      zoom: 1
    };
  });

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

  useEffect(() => {
    if (viewport) {
      localStorage.setItem('kgraph-viewport', JSON.stringify(viewport));
    }
  }, [viewport]);

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
          chat: null, // Set to null to trigger initial definition
          notes: '',
          quiz: []
        }
      },
      lastSelectedNodeId: timestamp
    };
    setGraphs([...graphs, newGraph]);
    setActiveGraph(newGraph);
  };

  const updateGraph = (updatedGraph, selectedNodeId = null) => {
    const graphToUpdate = {
      ...updatedGraph,
      lastSelectedNodeId: selectedNodeId || updatedGraph.lastSelectedNodeId
    };
    setGraphs(graphs.map(g => 
      g.id === graphToUpdate.id ? graphToUpdate : g
    ));
    setActiveGraph(graphToUpdate);
  };

  const updateViewport = (newViewport) => {
    // Validate viewport before updating
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

  const clearData = () => {
    localStorage.clear();
    setGraphs([]);
    setActiveGraph(null);
    setViewport({
      x: 0,
      y: 0,
      zoom: 1
    });
    return null; // Return null to clear selected node in parent
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
