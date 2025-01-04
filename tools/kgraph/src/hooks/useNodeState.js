import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition } from './useNodePosition';

export function useNodeState(activeGraph, updateGraph) {
  const { selectedNode, setSelectedNode, handleNodeClick } = useNodeSelection(activeGraph, updateGraph);
  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph);
  const { updateNodePosition } = useNodePosition(activeGraph, updateGraph);

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition
  };
}
