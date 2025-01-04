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
    // Validate graph structure
    if (!updatedGraph || !Array.isArray(updatedGraph.nodes) || !Array.isArray(updatedGraph.edges)) {
      console.error('Invalid graph structure:', updatedGraph);
      return;
    }

    // Ensure all nodes have valid IDs and positions
    const validNodes = updatedGraph.nodes.every(node => 
      node && node.id && node.position && 
      typeof node.position.x === 'number' && 
      typeof node.position.y === 'number'
    );

    if (!validNodes) {
      console.error('Invalid node data in graph');
      return;
    }

    // Ensure all edges have valid source and target
    const validEdges = updatedGraph.edges.every(edge =>
      edge && edge.source && edge.target &&
      updatedGraph.nodes.some(n => n.id === edge.source) &&
      updatedGraph.nodes.some(n => n.id === edge.target)
    );

    if (!validEdges) {
      console.error('Invalid edge data in graph');
      return;
    }

    // First, ensure we have the latest state
    setGraphs(prevGraphs => {
      const currentGraph = prevGraphs.find(g => g.id === updatedGraph.id);
      if (!currentGraph) return prevGraphs;

      // Handle node data updates
      const mergedNodeData = { ...currentGraph.nodeData };
      
      // First, handle any explicit nodeData updates
      if (updatedGraph.nodeData) {
        Object.assign(mergedNodeData, updatedGraph.nodeData);
      }
      
      // Then ensure all nodes have nodeData
      updatedGraph.nodes.forEach(node => {
        if (!mergedNodeData[node.id]) {
          // Initialize new nodes with null chat to trigger definition fetch
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

      // Create the final graph update
      const graphToUpdate = {
        ...updatedGraph,
        lastSelectedNodeId: selectedNodeId || updatedGraph.lastSelectedNodeId,
        nodeData: mergedNodeData
      };

      // Update graphs array
      const updatedGraphs = prevGraphs.map(g => 
        g.id === graphToUpdate.id ? graphToUpdate : g
      );

      // Persist to localStorage
      try {
        localStorage.setItem('kgraph-graphs', JSON.stringify(updatedGraphs));
        if (graphToUpdate.id) {
          localStorage.setItem('kgraph-last-graph', graphToUpdate.id.toString());
        }
      } catch (error) {
        console.error('Error persisting graph state:', error);
      }

      return updatedGraphs;
    });

    // Update active graph to match
    setActiveGraph(prevGraph => {
      if (prevGraph?.id !== updatedGraph.id) return prevGraph;
      
      return {
        ...updatedGraph,
        lastSelectedNodeId: selectedNodeId || updatedGraph.lastSelectedNodeId,
        nodeData: {
          ...prevGraph.nodeData,
          ...updatedGraph.nodeData
        }
      };
    });
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
