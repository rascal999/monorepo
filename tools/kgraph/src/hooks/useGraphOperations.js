import { useGraphValidation } from './useGraphValidation';

export function useGraphOperations(setGraphs, setActiveGraph) {
  const {
    validateGraph,
    validateGraphUpdate
  } = useGraphValidation();

  const deleteGraph = (graphId) => {
    setGraphs(prevGraphs => {
      const graphIndex = prevGraphs.findIndex(g => g.id === graphId);
      const newGraphs = prevGraphs.filter(g => g.id !== graphId);
      
      // Select the previous graph (or last graph if deleting first one)
      if (newGraphs.length > 0) {
        const newIndex = Math.min(graphIndex, newGraphs.length - 1);
        setActiveGraph(newGraphs[newIndex]);
      } else {
        setActiveGraph(null);
      }
      
      return newGraphs;
    });
  };

  const createGraph = (title) => {
    const timestamp = Date.now().toString();
    const newGraph = {
      id: parseInt(timestamp),
      title,
      nodes: [{
        id: timestamp,
        type: 'default',
        position: { x: 250, y: 100 },
        data: { 
          label: title,
          isLoading: false
        }
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

  const updateGraph = (updatedGraph, updatedNodeId) => {
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

      // Handle node positions
      const updatedNodes = updatedGraph.nodes.map(node => {
        // If this is a position update for a specific node, use the new position
        if (updatedNodeId && node.id === updatedNodeId) {
          return node;
        }
        // Otherwise preserve existing position
        const existingNode = currentGraph.nodes.find(n => n.id === node.id);
        return existingNode ? { ...node, position: existingNode.position } : node;
      });

      // Create the complete graph update
      const graphToUpdate = {
        ...updatedGraph,
        nodes: updatedNodes,
        lastSelectedNodeId: updatedGraph.lastSelectedNodeId || currentGraph.lastSelectedNodeId,
        nodeData: mergedNodeData
      };

      // Validate the complete update after merging nodeData
      if (!validateGraphUpdate(graphToUpdate, currentGraph)) {
        console.error('Invalid graph update');
        return prevGraphs;
      }

      // Update graphs array
      return prevGraphs.map(g => 
        g.id === graphToUpdate.id ? graphToUpdate : g
      );
    });

    // Update active graph to match
    setActiveGraph(prevGraph => {
      if (prevGraph?.id !== updatedGraph.id) return prevGraph;

      // Handle node positions
      const updatedNodes = updatedGraph.nodes.map(node => {
        // If this is a position update for a specific node, use the new position
        if (updatedNodeId && node.id === updatedNodeId) {
          return node;
        }
        // Otherwise preserve existing position
        const existingNode = prevGraph.nodes.find(n => n.id === node.id);
        return existingNode ? { ...node, position: existingNode.position } : node;
      });

      return {
        ...updatedGraph,
        nodes: updatedNodes,
        lastSelectedNodeId: updatedGraph.lastSelectedNodeId || prevGraph.lastSelectedNodeId,
        nodeData: {
          ...prevGraph.nodeData,
          ...updatedGraph.nodeData
        }
      };
    });
  };

  const setNodeLoading = (graphId, nodeId, isLoading) => {
    setGraphs(prevGraphs => {
      const graph = prevGraphs.find(g => g.id === graphId);
      if (!graph) return prevGraphs;

      const updatedNodes = graph.nodes.map(node => 
        node.id === nodeId 
          ? { ...node, data: { ...node.data, isLoading } }
          : node
      );

      const updatedGraph = { 
        ...graph, 
        nodes: updatedNodes,
        nodeData: graph.nodeData // Ensure nodeData is included
      };

      // Validate the update
      if (!validateGraphUpdate(updatedGraph, graph)) {
        console.error('Invalid graph update in setNodeLoading');
        return prevGraphs;
      }

      return prevGraphs.map(g => g.id === graphId ? updatedGraph : g);
    });

    // Update active graph if needed
    setActiveGraph(prevGraph => {
      if (prevGraph?.id !== graphId) return prevGraph;
      
      const updatedNodes = prevGraph.nodes.map(node => 
        node.id === nodeId 
          ? { ...node, data: { ...node.data, isLoading } }
          : node
      );

      return { 
        ...prevGraph, 
        nodes: updatedNodes,
        nodeData: prevGraph.nodeData // Ensure nodeData is included
      };
    });
  };

  return {
    createGraph,
    updateGraph,
    deleteGraph,
    setNodeLoading
  };
}
