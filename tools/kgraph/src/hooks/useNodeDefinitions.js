import { useNodeDefinitionsBatch } from './useNodeDefinitionsBatch';
import { useNodeDefinitionHandler } from './useNodeDefinitionHandler';

export function useNodeDefinitions(activeGraph, onUpdateData) {
  // Use both hooks to maintain functionality
  const { initializingNodes: batchInitializingNodes } = useNodeDefinitionsBatch(activeGraph, onUpdateData);
  const { initializingNodes: handlerInitializingNodes, handleGetDefinition } = useNodeDefinitionHandler(activeGraph, onUpdateData);

  // Combine initializing nodes from both hooks
  const initializingNodes = new Set([
    ...Array.from(batchInitializingNodes),
    ...Array.from(handlerInitializingNodes)
  ]);

  return {
    initializingNodes,
    handleGetDefinition
  };
}
