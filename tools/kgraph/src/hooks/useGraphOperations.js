import { useGraphValidation } from './useGraphValidation';

export function useGraphOperations(setGraphs, setActiveGraph, handleGetDefinition) {
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
    const newGraph = {
      id: parseInt(graphId),
      title,
      nodes: [{
        id: nodeId,
        type: 'default',
        position: { x: 250, y: 100 },
        data: { 
          label: title,
          isLoading: false
        }
      }],
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

    // Update graphs and set active
    setGraphs(prevGraphs => [...prevGraphs, graphWithLoading]);
    setActiveGraph(graphWithLoading);
  };

  const updateGraph = (updatedGraph, sourceNodeId) => {
    console.log('[GraphOperations] Updating graph:', {
      graphId: updatedGraph?.id,
      hasNodes: Array.isArray(updatedGraph?.nodes),
      nodeCount: updatedGraph?.nodes?.length,
      sourceNodeId,
      stack: new Error().stack
    });

    // Simple validation
    if (!updatedGraph?.id || !Array.isArray(updatedGraph.nodes)) {
      console.error('[GraphOperations] Invalid graph update:', {
        hasId: !!updatedGraph?.id,
        hasNodes: Array.isArray(updatedGraph?.nodes)
      });
      return;
    }

    // Update graphs array
    setGraphs(prevGraphs => {
      const newGraphs = prevGraphs.map(g => 
        g.id === updatedGraph.id ? updatedGraph : g
      );
      console.log('[GraphOperations] Updated graphs array:', {
        prevCount: prevGraphs.length,
        newCount: newGraphs.length,
        updatedGraphId: updatedGraph.id
      });
      return newGraphs;
    });

    // Update active graph
    setActiveGraph(prevGraph => {
      const shouldUpdate = prevGraph?.id === updatedGraph.id;
      console.log('[GraphOperations] Updating active graph:', {
        prevGraphId: prevGraph?.id,
        newGraphId: updatedGraph.id,
        shouldUpdate
      });
      return shouldUpdate ? updatedGraph : prevGraph;
    });
  };

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
          ? { ...node, data: { ...node.data, isLoading } }
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
      const newGraphs = prevGraphs.map(g => 
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
