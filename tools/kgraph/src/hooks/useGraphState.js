import { useState } from 'react';
import { useGraphPersistence } from './useGraphPersistence';
import { useViewportState } from './useViewportState';
import { useGraphValidation } from './useGraphValidation';

export function useGraphState() {
  // Load initial state from persistence
  const { loadInitialState } = useGraphPersistence();
  const initialState = loadInitialState();

  // Initialize state
  const [graphs, setGraphs] = useState(initialState.graphs);
  const [activeGraph, setActiveGraph] = useState(initialState.activeGraph);
  
  // Initialize viewport state
  const {
    viewport,
    updateViewport,
    resetViewport
  } = useViewportState(initialState.viewport);

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

      // Create the final graph update
      const graphToUpdate = {
        ...updatedGraph,
        lastSelectedNodeId: selectedNodeId || updatedGraph.lastSelectedNodeId,
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
        lastSelectedNodeId: selectedNodeId || updatedGraph.lastSelectedNodeId,
        nodeData: {
          ...prevGraph.nodeData,
          ...updatedGraph.nodeData
        }
      };
    });
  };

  const clearData = () => {
    setGraphs([]);
    setActiveGraph(null);
    resetViewport();
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
