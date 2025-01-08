export function useGraphLoading(setGraphs, setActiveGraph) {
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
    setNodeLoading
  };
}
