export function useNodePosition(activeGraph, updateGraph) {
  const updateNodePosition = (updatedNode) => {
    const updatedGraph = {
      ...activeGraph,
      nodes: activeGraph.nodes.map(n => 
        n.id === updatedNode.id ? updatedNode : n
      )
    };
    updateGraph(updatedGraph, updatedNode.id);
  };

  return { updateNodePosition };
}
