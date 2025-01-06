import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeData(activeGraph, updateGraph, setNodeLoading) {
  const updateNodeData = (nodeId, tabName, data, isDefinitionUpdate = false, lastUserSelectedNodeId = null) => {
    if (!activeGraph) return;

    // Update only the loading state for the target node, preserve all positions
    const updatedNodes = activeGraph.nodes.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          position: node.position, // Explicitly preserve Cytoscape position
          data: {
            ...node.data,
            isLoading: tabName === 'isLoadingDefinition' ? data : false
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
        [nodeId]: {
          ...activeGraph.nodeData[nodeId],
          // Handle chat data updates
        chat: tabName === 'chat' ? data : (activeGraph.nodeData[nodeId]?.chat || []),
        // Keep loading states in sync and ensure they're boolean
        isLoadingDefinition: tabName === 'isLoadingDefinition' ? Boolean(data) : false,
        // Preserve other data
        notes: activeGraph.nodeData[nodeId]?.notes || '',
        quiz: activeGraph.nodeData[nodeId]?.quiz || [],
        // Store chat scroll position
        chatScrollPosition: tabName === 'chatScrollPosition' ? data : (activeGraph.nodeData[nodeId]?.chatScrollPosition || 0)
        }
      }
    };

    // Ensure the node data exists in the graph before updating
    if (!activeGraph.nodeData[nodeId]) {
      updatedGraph.nodeData[nodeId] = {
        chat: tabName === 'chat' ? data : [],
        notes: '',
        quiz: [],
        isLoadingDefinition: tabName === 'isLoadingDefinition' ? Boolean(data) : false,
        chatScrollPosition: tabName === 'chatScrollPosition' ? data : 0
      };
    }

    // Update the graph with proper selection handling
    updateGraph({
      ...updatedGraph,
      lastSelectedNodeId: lastUserSelectedNodeId || (isDefinitionUpdate ? activeGraph.lastSelectedNodeId : nodeId)
    });
  };

  return { updateNodeData };
}
