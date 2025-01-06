import { useState, useEffect } from 'react';
import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition } from './useNodePosition';
import { useNodeInteraction } from './useNodeInteraction';
import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeState(activeGraph, updateGraph, setNodeLoading) {
  const { selectedNode, setSelectedNode, handleNodeClick: handleNodeClickBase } = useNodeSelection(activeGraph, updateGraph);
  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph, setNodeLoading);
  // Create wrapper for updateNodeData that includes lastUserSelectedNodeId
  const updateNodeDataWithSelection = (nodeId, tabName, data, isDefinitionUpdate = false) => {
    updateNodeData(nodeId, tabName, data, isDefinitionUpdate, lastUserSelectedNodeId);
  };

  // Pass updateNodeDataWithSelection and activeGraph to useNodeDefinitions
  const { handleGetDefinition, handleSendMessage } = useNodeDefinitions(
    activeGraph,
    updateNodeDataWithSelection,
    (graphId, nodeId, isLoading) => {
      console.log('Setting node loading state:', { graphId, nodeId, isLoading });
      setNodeLoading(graphId, nodeId, isLoading);
    }
  );
  const { updateNodePosition } = useNodePosition(activeGraph, updateGraph);

  // Track the last user-selected node ID, initialized from activeGraph
  const [lastUserSelectedNodeId, setLastUserSelectedNodeId] = useState(() => 
    activeGraph?.lastSelectedNodeId || null
  );

  // Update lastUserSelectedNodeId when switching graphs
  useEffect(() => {
    if (activeGraph?.lastSelectedNodeId) {
      setLastUserSelectedNodeId(activeGraph.lastSelectedNodeId);
    } else {
      setLastUserSelectedNodeId(null);
    }
  }, [activeGraph?.id]);

  // Manage tab state
  const [activeTab, setActiveTab] = useState('chat');

  // Create nodeInteraction instance
  const nodeInteraction = useNodeInteraction((sourceNode, term) => {
    console.log('useNodeState nodeInteraction callback called with:', {
      sourceNode: {
        id: sourceNode?.id,
        position: sourceNode?.position
      },
      term
    });

    const nodeId = addNode(sourceNode, term);
    console.log('useNodeState addNode result:', { nodeId });

    if (nodeId?.includes('-')) {
      console.log('useNodeState calling handleGetDefinition for nodeId:', nodeId);
      handleGetDefinition({ id: nodeId });
    }
    return nodeId;
  });

  return {
    selectedNode,
    setSelectedNode,
    activeTab,
    setActiveTab,
    nodeInteraction,
    handleSendMessage,
    handleNodeClick: handleNodeClickBase // Use handler from useNodeSelection
  };
}
