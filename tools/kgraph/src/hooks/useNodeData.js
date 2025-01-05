import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeData(activeGraph, updateGraph, setNodeLoading) {
  const updateNodeData = (nodeId, tabName, data, isDefinitionUpdate = false, lastUserSelectedNodeId = null) => {
    if (!activeGraph) return;

    // Create a deep copy of nodes to preserve positions
    const updatedNodes = activeGraph.nodes.map(node => ({
      ...node,
      position: { ...node.position }
    }));

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
