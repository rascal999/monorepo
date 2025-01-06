import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeData(activeGraph, updateGraph, setNodeLoading) {
  const updateNodeData = (nodeId, tabName, data, isDefinitionUpdate = false, lastUserSelectedNodeId = null) => {
    if (!activeGraph) return;

    // Create a map of current positions
    const nodePositions = {};
    activeGraph.nodes.forEach(node => {
      nodePositions[node.id] = { ...node.position };
    });

    // Only update the nodeData, leave nodes unchanged except for loading state
    const updatedNodes = activeGraph.nodes.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          position: nodePositions[node.id], // Preserve exact position
          data: {
            ...node.data,
            isLoading: tabName === 'isLoadingDefinition' ? data : false // Reset loading state unless explicitly setting it
          }
        };
      }
      return {
        ...node,
        position: nodePositions[node.id] // Preserve all node positions
      };
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
          quiz: activeGraph.nodeData[nodeId]?.quiz || []
        }
      }
    };

    // Ensure the node data exists in the graph before updating
    if (!activeGraph.nodeData[nodeId]) {
      updatedGraph.nodeData[nodeId] = {
        chat: tabName === 'chat' ? data : [],
        notes: '',
        quiz: [],
        isLoadingDefinition: tabName === 'isLoadingDefinition' ? Boolean(data) : false
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
