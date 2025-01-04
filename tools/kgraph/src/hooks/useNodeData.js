export function useNodeData(activeGraph, updateGraph) {
  const updateNodeData = (nodeId, tabName, data) => {
    if (!activeGraph) return;

    // Only update the nodeData without touching nodes or edges
    const updatedGraph = {
      ...activeGraph,
      nodes: activeGraph.nodes, // Explicitly preserve node positions
      nodeData: {
        ...activeGraph.nodeData,
        [nodeId]: {
          ...activeGraph.nodeData[nodeId],
          [tabName]: data
        }
      }
    };

    // Preserve the lastSelectedNodeId when updating chat data
    updateGraph(updatedGraph, activeGraph.lastSelectedNodeId);
  };

  return { updateNodeData };
}
