import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeData(activeGraph, updateGraph, setNodeLoading) {
  const updateNodeData = (nodeId, tabName, data, isDefinitionUpdate = false, lastUserSelectedNodeId = null) => {
    if (!activeGraph) {
      console.error('[NodeData] Cannot update - no active graph');
      return;
    }

    if (!nodeId) {
      console.error('[NodeData] Cannot update - no node ID provided');
      return;
    }

    // Debug current state
    console.log('[NodeData] Current state:', {
      graphId: activeGraph.id,
      nodeId,
      nodeDataKeys: Object.keys(activeGraph.nodeData),
      currentNodeData: activeGraph.nodeData[nodeId],
      isDefinitionUpdate
    });

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

    // Create updated node data with validation
    const updatedNodeData = {
      ...currentNodeData,
      ...updates,
      // Ensure chat is always an array
      chat: Array.isArray(updates.chat) ? updates.chat : currentNodeData.chat || []
    };

    // Debug node data update
    console.log('[NodeData] Node data update:', {
      nodeId,
      before: {
        chatLength: currentNodeData.chat?.length,
        isLoading: currentNodeData.isLoadingDefinition
      },
      after: {
        chatLength: updatedNodeData.chat?.length,
        isLoading: updatedNodeData.isLoadingDefinition
      }
    });

    // Update nodes with loading state
    const updatedNodes = activeGraph.nodes.map(node => 
      node.id === nodeId 
        ? {
            ...node,
            position: node.position,
            data: {
              ...node.data,
              isLoadingDefinition: 'isLoadingDefinition' in updates ? updates.isLoadingDefinition : node.data.isLoadingDefinition
            }
          }
        : node
    );

    // Create updated graph
    const updatedGraph = {
      ...activeGraph,
      nodes: updatedNodes,
      nodeData: {
        ...activeGraph.nodeData,
        [nodeId]: updatedNodeData
      },
      lastSelectedNodeId: lastUserSelectedNodeId || (isDefinitionUpdate ? activeGraph.lastSelectedNodeId : nodeId)
    };

    // Debug graph update
    console.log('[NodeData] Graph update:', {
      nodeId,
      nodeDataKeys: Object.keys(updatedGraph.nodeData),
      hasChat: Boolean(updatedGraph.nodeData[nodeId]?.chat),
      chatLength: updatedGraph.nodeData[nodeId]?.chat?.length,
      lastSelectedNodeId: updatedGraph.lastSelectedNodeId
    });

    updateGraph(updatedGraph);
  };

  return { updateNodeData };
}
