import { useState } from 'react';
import { aiService } from '../services/ai';

export function useNodeDefinitionHandler(activeGraph, onUpdateData) {
  const [initializingNodes, setInitializingNodes] = useState(new Set());

  const handleGetDefinition = async (targetNode, graphId) => {
    console.log('handleGetDefinition called with:', {
      nodeId: targetNode?.id,
      label: targetNode?.data?.label,
      graphId
    });

    // Validate target node exists in current graph
    if (!targetNode?.id || !targetNode?.data?.label || !activeGraph?.nodes?.find(n => n.id === targetNode.id)) {
      console.error('Invalid or missing target node:', {
        hasId: !!targetNode?.id,
        hasLabel: !!targetNode?.data?.label,
        existsInGraph: !!activeGraph?.nodes?.find(n => n.id === targetNode?.id)
      });
      return;
    }
    
    // Skip if already initializing
    if (initializingNodes.has(targetNode.id)) {
      console.log('Node already initializing:', targetNode.id);
      // Clear loading state since we're skipping
      onUpdateData(targetNode.id, 'isLoadingDefinition', false);
      return;
    }
    
    // Use provided graphId or fall back to activeGraph.id
    const effectiveGraphId = graphId || activeGraph?.id;
    if (!effectiveGraphId) {
      console.error('No graph ID available for definition request');
      return;
    }

    try {
      // Set loading state only if not already loaded
      console.log('Setting loading state for node:', targetNode.id);
      if (!activeGraph.nodeData[targetNode.id]?.chat?.length) {
        onUpdateData(targetNode.id, 'isLoadingDefinition', true);
        setInitializingNodes(prev => new Set([...prev, targetNode.id]));
      }

      // Verify node still exists before proceeding
      if (!activeGraph?.nodes?.find(n => n.id === targetNode.id)) {
        throw new Error('Node no longer exists in graph');
      }

      // Return a promise that resolves when definition is complete
      return new Promise((resolve, reject) => {
        console.log('Queueing definition request for:', targetNode.data.label);
        aiService.queueDefinitionRequest(
          targetNode.data.label,
          activeGraph.title,
          (result) => {
            try {
              // Verify node still exists before updating
              if (!activeGraph?.nodes?.find(n => n.id === targetNode.id)) {
                console.error('Node no longer exists, skipping update');
                reject(new Error('Node no longer exists'));
                return;
              }

              // Update chat data and clear loading state
              if (result.success) {
                const formattedMessage = {
                  role: result.message.role || 'assistant',
                  content: result.message.content
                };
                // Update chat data and loading state in a single operation
                onUpdateData(targetNode.id, null, {
                  chat: [formattedMessage],
                  isLoadingDefinition: false
                }, true);
              } else {
                // Update chat with error and loading state in a single operation
                onUpdateData(targetNode.id, null, {
                  chat: [{
                    role: 'assistant',
                    content: 'Error fetching definition. Please check your API key and try again.'
                  }],
                  isLoadingDefinition: false
                }, true);
              }
              resolve();
            } catch (error) {
              console.error('Error updating node data:', error);
              reject(error);
            } finally {
              // Always clean up initializing state
              setInitializingNodes(prev => {
                const next = new Set(prev);
                next.delete(targetNode.id);
                return next;
              });
            }
          }
        );
      });
    } catch (error) {
      console.error('Error in handleGetDefinition:', error);
      // Ensure loading states are cleared on error
      onUpdateData(targetNode.id, 'isLoadingDefinition', false);
      setInitializingNodes(prev => {
        const next = new Set(prev);
        next.delete(targetNode.id);
        return next;
      });
      throw error; // Re-throw to be handled by caller
    }
  };

  return {
    initializingNodes,
    handleGetDefinition
  };
}
