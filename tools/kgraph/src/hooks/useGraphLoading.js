export function useGraphLoading(setGraphs, setActiveGraph) {
  const setNodeLoading = (graphId, nodeId, isLoading) => {
    console.log('[GraphLoading] Setting node loading state:', {
      graphId,
      nodeId,
      isLoading,
      timestamp: Date.now()
    });

    const createUpdatedGraph = (graph) => {
      if (!graph) return graph;

      const updatedNodes = graph.nodes.map(node => 
        node.id === nodeId 
          ? { ...node, data: { ...node.data, isLoadingDefinition: isLoading } }
          : node
      );

      console.log('[GraphLoading] Current node state:', {
        nodeId,
        currentNodeData: graph.nodeData[nodeId],
        currentNodeState: graph.nodes.find(n => n.id === nodeId)?.data
      });

      // Update both node.data and nodeData
      const updatedNodeData = {
        ...graph.nodeData,
        [nodeId]: {
          ...graph.nodeData[nodeId],
          isLoadingDefinition: isLoading
        }
      };

      const updatedGraph = {
        ...graph,
        nodes: updatedNodes,
        nodeData: updatedNodeData
      };

      console.log('[GraphLoading] Updated node state:', {
        nodeId,
        updatedNodeData: updatedNodeData[nodeId],
        updatedNodeState: updatedNodes.find(n => n.id === nodeId)?.data
      });

      return updatedGraph;
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
