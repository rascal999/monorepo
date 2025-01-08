import { useCallback } from 'react';
import { useGraphValidation } from './useGraphValidation';

export function useGraphCRUD(graphs, setGraphs, setActiveGraph) {
  const {
    validateGraph,
    validateGraphUpdate
  } = useGraphValidation();

  const deleteGraph = (graphId) => {
    console.log('[GraphOperations] Deleting graph', graphId);

    // Clean up viewport data for the deleted graph
    localStorage.removeItem(`kgraph-viewport-${graphId}`);

    setGraphs(prevGraphs => {
      const graphIndex = prevGraphs.findIndex(g => g.id === graphId);
      const newGraphs = prevGraphs.filter(g => g.id !== graphId);
      
      // Select the previous graph (or last graph if deleting first one)
      if (newGraphs.length > 0) {
        const newIndex = Math.min(graphIndex, newGraphs.length - 1);
        const nextGraph = newGraphs[newIndex];
        console.log('[GraphOperations] Switching to graph', nextGraph.id);
        // Load saved viewport for next graph
        setActiveGraph(nextGraph);
      } else {
        console.log('[GraphOperations] No graphs left, clearing active graph');
        setActiveGraph(null);
      }
      
      return newGraphs;
    });
  };

  const createGraph = (title) => {
    console.log('[GraphOperations] Creating new graph', title);
    const graphId = Date.now().toString();
    const nodeId = (Date.now() + 1).toString(); // Ensure unique ID by adding 1
    // Create initial node with title as label
    const initialNode = {
      id: nodeId,
      type: 'default',
      position: { x: 250, y: 100 },
      data: { 
        label: title,
        isLoadingDefinition: true
      }
    };

    const newGraph = {
      id: parseInt(graphId),
      title: title, // Set graph title to match initial node label
      nodes: [initialNode],
      edges: [],
      nodeData: {
        [nodeId]: {
          chat: [],
          notes: '',
          quiz: [],
          isLoadingDefinition: true
        }
      },
      lastSelectedNodeId: nodeId
    };

    if (!validateGraph(newGraph)) {
      console.error('Invalid graph structure in createGraph');
      return;
    }

    // Create graph with loading state
    const graphWithLoading = {
      ...newGraph,
      nodeData: {
        [nodeId]: {
          ...newGraph.nodeData[nodeId],
          isLoadingDefinition: true
        }
      }
    };

    // Update graphs and set active synchronously
    setGraphs(prevGraphs => {
      const newGraphs = [...prevGraphs, graphWithLoading];
      // Set active graph immediately
      setActiveGraph(graphWithLoading);
      return newGraphs;
    });

    // Return the graph ID so it can be used immediately
    return graphWithLoading.id;
  };

  const updateGraph = useCallback((updatedGraph, sourceNodeId) => {
    // Basic validation
    if (!updatedGraph?.id || !Array.isArray(updatedGraph.nodes)) {
      console.warn('[GraphOperations] Invalid graph update');
      return;
    }

    // Helper function to wait
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Find existing graph with retry
    const findGraph = async (retries = 3, delay = 50) => {
      for (let i = retries; i >= 0; i--) {
        const existingGraph = graphs.find(g => g.id === updatedGraph.id);
        if (existingGraph) {
          return existingGraph;
        }
        if (i > 0) {
          console.log('[GraphOperations] Graph not found, retrying...', {
            graphId: updatedGraph.id,
            remainingRetries: i - 1
          });
          await wait(delay);
        }
      }
      console.warn('[GraphOperations] Graph not found after retries:', updatedGraph.id);
      return null;
    };

    // Use async/await to handle the graph update
    (async () => {
      const existingGraph = await findGraph();
      if (!existingGraph) {
        return;
      }

      // Continue with graph update...
      // Validate all nodes have required data
      const hasInvalidNodes = updatedGraph.nodes.some(node => 
        !node?.id || !node?.data?.label || !node?.position?.x || !node?.position?.y
      );

      if (hasInvalidNodes) {
        console.error('[GraphOperations] Invalid node data in update:', 
          updatedGraph.nodes.map(n => ({
            id: n?.id,
            hasData: !!n?.data,
            hasLabel: !!n?.data?.label,
            hasPosition: !!(n?.position?.x && n?.position?.y)
          }))
        );
        return;
      }

      // Merge nodeData from existing graph
      const mergedNodeData = { ...existingGraph.nodeData };
      
      // Add any new nodeData
      updatedGraph.nodes.forEach(node => {
        if (!mergedNodeData[node.id]) {
          mergedNodeData[node.id] = {
            chat: [],
            notes: '',
            quiz: [],
            isLoadingDefinition: true
          };
        }
      });

      // Create merged graph
      const mergedGraph = {
        ...updatedGraph,
        nodeData: mergedNodeData
      };

      // Update graphs array first
      setGraphs(prevGraphs => {
        const currentGraphs = Array.isArray(prevGraphs) ? prevGraphs : [];
        return currentGraphs.map(g => 
          g.id === mergedGraph.id ? mergedGraph : g
        );
      });

      // Then update active graph if it matches
      setActiveGraph(prevGraph => {
        if (prevGraph?.id !== mergedGraph.id) return prevGraph;
        return mergedGraph;
      });
    })().catch(error => {
      console.error('[GraphOperations] Error updating graph:', error);
    });
  }, [setGraphs, setActiveGraph]);

  const setNodeLoading = (graphId, nodeId, isLoading) => {
    console.log('[GraphOperations] Setting node loading state:', {
      graphId,
      nodeId,
      isLoading
    });

    const createUpdatedGraph = (graph) => {
      if (!graph) return graph;

      const updatedNodes = graph.nodes.map(node => 
        node.id === nodeId 
          ? { ...node, data: { ...node.data, isLoadingDefinition: isLoading } }
          : node
      );

      return {
        ...graph,
        nodes: updatedNodes,
        nodeData: graph.nodeData
      };
    };

    // Update graphs array
    setGraphs(prevGraphs => {
      // Ensure prevGraphs is an array
      const currentGraphs = Array.isArray(prevGraphs) ? prevGraphs : [];
      const newGraphs = currentGraphs.map(g => 
        g.id === graphId ? createUpdatedGraph(g) : g
      );
      return newGraphs;
    });

    // Update active graph if it matches
    setActiveGraph(prevGraph => {
      if (prevGraph?.id !== graphId) return prevGraph;
      return createUpdatedGraph(prevGraph);
    });
  };

  return {
    createGraph,
    updateGraph,
    deleteGraph,
    setNodeLoading
  };
}
