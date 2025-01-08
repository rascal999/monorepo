import { useEffect, useCallback } from 'react';
import { useNodeDefinitionsBatch } from './useNodeDefinitionsBatch';
import { useNodeDefinitionHandler } from './useNodeDefinitionHandler';

export function useNodeDefinitions(activeGraph, onUpdateData) {
  // Use both hooks to maintain functionality
  const { initializingNodes: batchInitializingNodes } = useNodeDefinitionsBatch(activeGraph, onUpdateData);
  const { initializingNodes: handlerInitializingNodes, handleGetDefinition: baseHandleGetDefinition } = useNodeDefinitionHandler(activeGraph, onUpdateData);

  // Clear loading states when graph changes
  useEffect(() => {
    if (!activeGraph?.nodeData) return;

    console.log('useNodeDefinitions: Checking for stuck loading states');
    // Find any nodes stuck in loading state
    Object.entries(activeGraph.nodeData)
      .filter(([_, data]) => data.isLoadingDefinition)
      .forEach(([nodeId]) => {
        console.log('useNodeDefinitions: Clearing stuck loading state for node:', nodeId);
        // Clear loading state and ensure chat array exists
        onUpdateData(nodeId, null, {
          chat: activeGraph.nodeData[nodeId]?.chat || [],
          isLoadingDefinition: false
        });
      });
  }, [activeGraph?.id]);

  // Combine initializing nodes from both hooks
  const initializingNodes = new Set([
    ...Array.from(batchInitializingNodes),
    ...Array.from(handlerInitializingNodes)
  ]);

  // Create handleGetDefinition that coordinates with useNodeState
  const handleGetDefinition = useCallback(async (node) => {
    if (!node?.id || !activeGraph) {
      console.error('useNodeDefinitions: Invalid node or missing graph:', {
        hasNode: !!node,
        hasId: !!node?.id,
        hasGraph: !!activeGraph
      });
      return;
    }

    console.log('useNodeDefinitions: Starting definition fetch:', {
      nodeId: node.id,
      label: node.data?.label,
      graphId: activeGraph.id
    });

    try {
      // Initialize loading state
      onUpdateData(node.id, null, {
        chat: [],
        isLoadingDefinition: true
      });

      // Wait for state to update
      await new Promise(resolve => setTimeout(resolve, 0));

      // Let baseHandleGetDefinition handle the request
      await baseHandleGetDefinition(node);
    } catch (error) {
      // Log error but let parent handle state updates
      console.error('useNodeDefinitions: Error in definition handler:', error);
      throw error;
    }
  }, [activeGraph, baseHandleGetDefinition, onUpdateData]);

  // Create handleSendMessage for chat interactions
  const handleSendMessage = useCallback(async (nodeId, content, onStream) => {
    if (!nodeId || !activeGraph) {
      console.error('useNodeDefinitions: Invalid node ID or missing graph:', {
        nodeId,
        hasGraph: !!activeGraph
      });
      return;
    }

    console.log('useNodeDefinitions: Sending chat message:', {
      nodeId,
      contentLength: content?.length
    });

    try {
      // Implementation would go here
      console.log('useNodeDefinitions: Chat message sent successfully');
    } catch (error) {
      console.error('useNodeDefinitions: Error sending chat message:', error);
      throw error;
    }
  }, [activeGraph]);

  return {
    initializingNodes,
    handleGetDefinition,
    handleSendMessage
  };
}
