import { useState, useEffect } from 'react';
import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition as importedUseNodePosition } from './useNodePosition';
import { useNodeInteraction } from './useNodeInteraction';
import { useNodeDefinitions } from './useNodeDefinitions';

// Create validated version of useNodePosition
const useNodePosition = (activeGraph, updateGraph) => {
  console.log('useNodePosition called with:', {
    hasActiveGraph: !!activeGraph,
    hasUpdateGraph: !!updateGraph
  });

  const result = importedUseNodePosition(activeGraph, updateGraph);
  
  console.log('useNodePosition result:', {
    hasResult: !!result,
    hasUpdateNodePosition: result?.updateNodePosition !== undefined,
    updateNodePositionType: typeof result?.updateNodePosition
  });

  if (!result || typeof result.updateNodePosition !== 'function') {
    console.error('useNodePosition hook returned invalid result');
    // Return a default implementation to prevent undefined errors
    return {
      updateNodePosition: (update) => {
        console.error('Called fallback updateNodePosition:', update);
      }
    };
  }

  return result;
};

export function useNodeState(activeGraph, updateGraph, setNodeLoading, graphs) {
  console.log('[NodeState] Initializing with:', {
    activeGraphId: activeGraph?.id,
    lastSelectedNodeId: activeGraph?.lastSelectedNodeId,
    hasNodes: activeGraph?.nodes?.length,
    stack: new Error().stack
  });

  const { selectedNode, setSelectedNode, handleNodeClick: handleNodeClickBase } = useNodeSelection(activeGraph, updateGraph, graphs);

  // Add effect to monitor selectedNode changes
  useEffect(() => {
    console.log('[NodeState] Selected node changed:', {
      hasSelectedNode: !!selectedNode,
      nodeId: selectedNode?.id,
      nodeLabel: selectedNode?.data?.label,
      activeGraphId: activeGraph?.id,
      lastSelectedNodeId: activeGraph?.lastSelectedNodeId
    });
  }, [selectedNode, activeGraph]);

  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph, setNodeLoading);

  // Track the last user-selected node ID
  const [lastUserSelectedNodeId, setLastUserSelectedNodeId] = useState(null);

  // Create wrapper for updateNodeData that includes lastUserSelectedNodeId
  const updateNodeDataWithSelection = (nodeId, tabName, data, isDefinitionUpdate = false) => {
    // Only pass lastUserSelectedNodeId if it's not null/undefined and different from nodeId
    const selectionId = lastUserSelectedNodeId && lastUserSelectedNodeId !== nodeId ? lastUserSelectedNodeId : null;
    updateNodeData(nodeId, tabName, data, isDefinitionUpdate, selectionId);
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

  // Initialize node position handling
  const nodePosition = useNodePosition(activeGraph, updateGraph);
  const updateNodePosition = nodePosition?.updateNodePosition;

  // Validate updateNodePosition is a function
  useEffect(() => {
    if (typeof updateNodePosition !== 'function') {
      console.error('updateNodePosition is not a function:', {
        type: typeof updateNodePosition,
        value: updateNodePosition,
        hasActiveGraph: !!activeGraph,
        hasUpdateGraph: !!updateGraph
      });
    }
  }, [updateNodePosition, activeGraph, updateGraph]);

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
    handleNodeClick: handleNodeClickBase,
    addNode,
    updateNodeData: updateNodeDataWithSelection,
    updateNodePosition,
    handleGetDefinition
  };
}
