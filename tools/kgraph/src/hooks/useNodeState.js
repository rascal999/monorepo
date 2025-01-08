import { useState, useEffect, useRef, useCallback } from 'react';
import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition as importedUseNodePosition } from './useNodePosition';
import { useNodeInteraction } from './useNodeInteraction';
import { useNodeDefinitions } from './useNodeDefinitions';

// Create validated version of useNodePosition
const useNodePosition = (activeGraph, updateGraph) => {
  const result = importedUseNodePosition(activeGraph, updateGraph);
  
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
  const { selectedNode, setSelectedNode, handleNodeClick: handleNodeClickBase } = useNodeSelection(activeGraph, updateGraph, graphs);
  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph, setNodeLoading);

  // Track the last user-selected node ID
  const [lastUserSelectedNodeId, setLastUserSelectedNodeId] = useState(null);

  // Create wrapper for updateNodeData that includes lastUserSelectedNodeId
  const updateNodeDataWithSelection = useCallback((nodeId, tabName, data, isDefinitionUpdate = false) => {
    const selectionId = lastUserSelectedNodeId && lastUserSelectedNodeId !== nodeId ? lastUserSelectedNodeId : null;
    updateNodeData(nodeId, tabName, data, isDefinitionUpdate, selectionId);
  }, [lastUserSelectedNodeId, updateNodeData]);

  // Pass updateNodeDataWithSelection and activeGraph to useNodeDefinitions
  const { handleSendMessage } = useNodeDefinitions(
    activeGraph,
    updateNodeDataWithSelection,
    setNodeLoading
  );

  // Initialize node position handling
  const nodePosition = useNodePosition(activeGraph, updateGraph);
  const updateNodePosition = nodePosition?.updateNodePosition;

  // Validate updateNodePosition is a function
  useEffect(() => {
    if (typeof updateNodePosition !== 'function') {
      console.error('updateNodePosition is not a function:', {
        type: typeof updateNodePosition,
        hasActiveGraph: !!activeGraph,
        hasUpdateGraph: !!updateGraph
      });
    }
  }, [updateNodePosition, activeGraph, updateGraph]);

  // Manage tab state
  const [activeTab, setActiveTab] = useState('chat');

  const nodeInteraction = useNodeInteraction((sourceNode, term) => {
    const nodeId = addNode(sourceNode, term);
    
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
  };
}
