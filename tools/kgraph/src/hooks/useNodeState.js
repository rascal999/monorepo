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

  // Debug current node state
  useEffect(() => {
    if (activeGraph && selectedNode) {
      console.log('[NodeState] Current state:', {
        selectedNodeId: selectedNode.id,
        nodeData: activeGraph.nodeData[selectedNode.id],
        lastUserSelected: lastUserSelectedNodeId
      });
    }
  }, [activeGraph, selectedNode, lastUserSelectedNodeId]);

  // Manage tab state
  const [activeTab, setActiveTab] = useState('chat');

  // Create wrapper for updateNodeData that includes lastUserSelectedNodeId
  const updateNodeDataWithSelection = useCallback((nodeId, tabName, data, isDefinitionUpdate = false) => {
    console.log('[NodeState] Updating node data:', {
      nodeId,
      tabName,
      isDefinition: isDefinitionUpdate,
      currentData: activeGraph?.nodeData[nodeId],
      newData: data
    });

    const selectionId = lastUserSelectedNodeId && lastUserSelectedNodeId !== nodeId ? lastUserSelectedNodeId : null;
    updateNodeData(nodeId, tabName, data, isDefinitionUpdate, selectionId);

    // Force tab switch on definition update
    if (isDefinitionUpdate) {
      console.log('[NodeState] Switching to chat tab');
      setActiveTab('chat');
    }
  }, [lastUserSelectedNodeId, updateNodeData, activeGraph]);

  // Pass updateNodeDataWithSelection and activeGraph to useNodeDefinitions
  const { handleSendMessage } = useNodeDefinitions(
    activeGraph,
    updateNodeDataWithSelection,
    setNodeLoading
  );

  // Handle node selection
  const handleNodeClick = useCallback((node) => {
    console.log('[NodeState] Node clicked:', {
      id: node.id,
      label: node.data.label,
      hasChat: Boolean(activeGraph?.nodeData[node.id]?.chat)
    });
    
    setLastUserSelectedNodeId(node.id);
    handleNodeClickBase(node);
  }, [activeGraph, handleNodeClickBase]);

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

  const nodeInteraction = useNodeInteraction((sourceNode, term) => {
    const nodeId = addNode(sourceNode, term);
    
    return nodeId;
  });

  // Debug return values
  const returnValues = {
    selectedNode,
    setSelectedNode,
    activeTab,
    setActiveTab,
    nodeInteraction,
    handleSendMessage,
    handleNodeClick,  // Use our wrapped version
    addNode,
    updateNodeData: updateNodeDataWithSelection,
    updateNodePosition,
  };

  // Log state on changes
  useEffect(() => {
    console.log('[NodeState] State updated:', {
      hasSelectedNode: Boolean(selectedNode),
      activeTab,
      hasNodeInteraction: Boolean(nodeInteraction),
      hasHandleClick: Boolean(handleNodeClick),
      hasUpdateData: Boolean(updateNodeDataWithSelection)
    });
  }, [selectedNode, activeTab, nodeInteraction, handleNodeClick, updateNodeDataWithSelection]);

  return returnValues;
}
