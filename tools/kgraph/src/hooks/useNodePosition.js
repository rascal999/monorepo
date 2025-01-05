export function useNodePosition(activeGraph, updateGraph) {
  const updateNodePosition = (updatedNode) => {
    // Find the node to update
    const nodeToUpdate = activeGraph.nodes.find(node => node.id === updatedNode.id);
    if (!nodeToUpdate) return;

    // Create updated graph with new position
    const updatedGraph = {
      ...activeGraph,
      nodes: activeGraph.nodes.map(node => 
        node.id === updatedNode.id 
          ? { ...nodeToUpdate, position: updatedNode.position }
          : node
      )
    };

    // Pass the node ID to indicate this is a position update
    updateGraph(updatedGraph, updatedNode.id);
  };

  return { updateNodePosition };
}
