import { useState, useEffect } from 'react';
import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition } from './useNodePosition';
import { useNodeInteraction } from './useNodeInteraction';

export function useNodeState(activeGraph, updateGraph) {
  const { selectedNode, setSelectedNode, handleNodeClick: handleNodeClickBase } = useNodeSelection(activeGraph, updateGraph);
  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph);
  const { updateNodePosition } = useNodePosition(activeGraph, updateGraph);

  // Manage tab state
  const [activeTab, setActiveTab] = useState('chat');

  // Create single instance of useNodeInteraction
  const nodeInteraction = useNodeInteraction(addNode);
  const { handleNodeSelect } = nodeInteraction;

  // Switch to chat tab when selected node changes
  useEffect(() => {
    if (selectedNode) {
      console.log('useNodeState selectedNode changed, switching to chat tab');
      setActiveTab('chat');
    }
  }, [selectedNode]);

  const handleNodeClick = (node) => {
    console.log('useNodeState handleNodeClick:', { node });
    handleNodeClickBase(node);
    console.log('useNodeState after handleNodeClickBase');
    handleNodeSelect();
    console.log('useNodeState after handleNodeSelect');
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition,
    activeTab,
    setActiveTab,
    nodeInteraction
  };
}
