import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeData(activeGraph, updateGraph, setNodeLoading) {
  const updateNodeData = (nodeId, tabName, data, isDefinitionUpdate = false, lastUserSelectedNodeId = null) => {
    if (!activeGraph) return;

    // Handle batch updates when tabName is null and data is an object of updates
    const updates = tabName === null && typeof data === 'object' ? data : {
      [tabName]: data
    };

    // Get current node data with defaults
    const currentNodeData = activeGraph.nodeData[nodeId] || {
      chat: [],
      notes: '',
      quiz: [],
      isLoadingDefinition: false,
      chatScrollPosition: 0
    };

    // Create updated node data
    const updatedNodeData = {
      ...currentNodeData,
      ...updates
    };

    // Ensure chat array exists
    if (!Array.isArray(updatedNodeData.chat)) {
      updatedNodeData.chat = [];
    }

    // Only update nodes if there's a change in loading state
    let updatedNodes = activeGraph.nodes;
    if ('isLoadingDefinition' in updates) {
      updatedNodes = activeGraph.nodes.map(node => {
        if (node.id === nodeId) {
          return {
            ...node,
            position: node.position, // Explicitly preserve Cytoscape position
            data: {
              ...node.data,
              isLoadingDefinition: updates.isLoadingDefinition
            }
          };
        }
        return node;
      });
    }

    // Create updated graph with new node data
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
