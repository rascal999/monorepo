import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeData(activeGraph, updateGraph, setNodeLoading) {
  const updateNodeData = (nodeId, tabName, data, isDefinitionUpdate = false, lastUserSelectedNodeId = null) => {
    if (!activeGraph) return;

    // Handle batch updates when tabName is null and data is an object of updates
    const updates = tabName === null && typeof data === 'object' ? data : {
      [tabName]: data
    };

    // Update node data with all changes
    const currentNodeData = activeGraph.nodeData[nodeId] || {
      chat: [],
      notes: '',
      quiz: [],
      isLoadingDefinition: false,
      chatScrollPosition: 0
    };

    const updatedNodeData = {
      ...currentNodeData,
      ...updates
    };

    // Update node loading state
    const updatedNodes = activeGraph.nodes.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          position: node.position, // Explicitly preserve Cytoscape position
          data: {
            ...node.data,
            isLoadingDefinition: updatedNodeData.isLoadingDefinition
          }
        };
      }
      return node;
    });

    const updatedGraph = {
      ...activeGraph,
      nodes: updatedNodes,
      nodeData: {
        ...activeGraph.nodeData,
        [nodeId]: updatedNodeData
      }
    };

    // Update the graph with proper selection handling
    updateGraph({
      ...updatedGraph,
      lastSelectedNodeId: lastUserSelectedNodeId || (isDefinitionUpdate ? activeGraph.lastSelectedNodeId : nodeId)
    });
  };

  return { updateNodeData };
}
