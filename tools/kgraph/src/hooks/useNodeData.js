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
            isLoading: tabName === 'chat' // Only update loading state for chat updates
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
          [tabName]: data
        }
      }
    };

    // Always respect the last user-selected node if available
    if (lastUserSelectedNodeId) {
      updateGraph({
        ...updatedGraph,
        lastSelectedNodeId: lastUserSelectedNodeId
      });
    } else if (isDefinitionUpdate) {
      // For definition updates without user selection, preserve current selection
      updateGraph({
        ...updatedGraph,
        lastSelectedNodeId: activeGraph.lastSelectedNodeId
      });
    } else {
      // For normal updates without user selection, let the selection change
      updateGraph(updatedGraph);
    }
  };

  return { updateNodeData };
}
