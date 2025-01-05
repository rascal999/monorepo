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
  const { activeTab, setActiveTab, handleNodeSelect } = useNodeInteraction(addNode);

  const handleNodeClick = (node) => {
    console.log('useNodeState handleNodeClick:', { node });
    handleNodeClickBase(node);
    console.log('useNodeState after handleNodeClickBase');
    handleNodeSelect();
    console.log('useNodeState after handleNodeSelect');
    setActiveTab('chat');
    console.log('useNodeState after setActiveTab');
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition,
    activeTab,
    setActiveTab
  };
}
