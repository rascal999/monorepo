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
  const { handleNodeSelect } = useNodeInteraction(addNode);

  const handleNodeClick = (node) => {
    handleNodeClickBase(node);
    handleNodeSelect();
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition
  };
}
