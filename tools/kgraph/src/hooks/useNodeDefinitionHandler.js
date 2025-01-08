import { useState, useEffect } from 'react';
import { aiService } from '../services/ai';

export function useNodeDefinitionHandler(activeGraph, onUpdateData) {
  // Track nodes being initialized
  const [initializingNodes, setInitializingNodes] = useState(new Set());

  // Clear stale requests when graph changes
  useEffect(() => {
    if (!activeGraph) return;

    console.log('useNodeDefinitionHandler: Graph changed, cleaning up requests');
    aiService.clearStaleRequests();

    // Clean up any stuck loading states
    Object.entries(activeGraph.nodeData || {})
      .filter(([_, data]) => data.isLoadingDefinition)
      .forEach(([nodeId]) => {
        console.log('useNodeDefinitionHandler: Clearing stuck loading state:', nodeId);
        onUpdateData(nodeId, null, {
          chat: activeGraph.nodeData[nodeId]?.chat || [],
          isLoadingDefinition: false
        });
      });
  }, [activeGraph?.id]);

  const handleGetDefinition = async (targetNode, graphId) => {
    console.log('useNodeDefinitionHandler: Starting definition fetch:', {
      nodeId: targetNode?.id,
      label: targetNode?.data?.label,
      graphId
    });

    // Validate target node exists in current graph
    if (!targetNode?.id || !targetNode?.data?.label || !activeGraph?.nodes?.find(n => n.id === targetNode.id)) {
      console.error('useNodeDefinitionHandler: Invalid or missing target node:', {
        hasId: !!targetNode?.id,
        hasLabel: !!targetNode?.data?.label,
        existsInGraph: !!activeGraph?.nodes?.find(n => n.id === targetNode?.id)
      });
      return;
    }
    
    // Skip if already initializing
    if (initializingNodes.has(targetNode.id)) {
      console.log('useNodeDefinitionHandler: Node already initializing:', targetNode.id);
      return;
    }
    
    // Use provided graphId or fall back to activeGraph.id
    const effectiveGraphId = graphId || activeGraph?.id;
    if (!effectiveGraphId) {
      console.error('useNodeDefinitionHandler: No graph ID available');
      return;
    }

    try {
      // Track initializing state
      setInitializingNodes(prev => new Set([...prev, targetNode.id]));

      // Initialize chat array and set loading state
      onUpdateData(targetNode.id, null, {
        chat: [],
        isLoadingDefinition: true
      });

      // Verify node still exists before proceeding
      if (!activeGraph?.nodes?.find(n => n.id === targetNode.id)) {
        throw new Error('Node no longer exists in graph');
      }

      // Return a promise that resolves when definition is complete
      return new Promise((resolve, reject) => {
        console.log('useNodeDefinitionHandler: Queueing definition request:', {
          nodeId: targetNode.id,
          label: targetNode.data.label
        });

        aiService.queueDefinitionRequest(
          targetNode.data.label,
          activeGraph.title,
          (result) => {
            try {
              // Verify node still exists before updating
              if (!activeGraph?.nodes?.find(n => n.id === targetNode.id)) {
                console.error('useNodeDefinitionHandler: Node no longer exists');
                reject(new Error('Node no longer exists'));
                return;
              }

              // Update chat data and ensure loading state is cleared
              if (result.success && result.message) {
                const formattedMessage = {
                  role: result.message.role || 'assistant',
                  content: result.message.content || ''
                };
                onUpdateData(targetNode.id, null, {
                  chat: [formattedMessage],
                  isLoadingDefinition: false
                }, true);
                resolve();
              } else {
                console.error('useNodeDefinitionHandler: Definition request failed:', result.error);
                onUpdateData(targetNode.id, null, {
                  chat: [{
                    role: 'assistant',
                    content: 'Error fetching definition. Please check your API key and try again.'
                  }],
                  isLoadingDefinition: false
                }, true);
                reject(new Error(result.error || 'Definition request failed'));
              }
            } catch (error) {
              console.error('useNodeDefinitionHandler: Error updating node data:', error);
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
      console.error('useNodeDefinitionHandler: Error in definition handler:', error);
      // Clean up state
      onUpdateData(targetNode.id, null, {
        chat: [{
          role: 'assistant',
          content: 'Error fetching definition. Please try again.'
        }],
        isLoadingDefinition: false
      });
      setInitializingNodes(prev => {
        const next = new Set(prev);
        next.delete(targetNode.id);
        return next;
      });
      throw error; // Re-throw to let parent handle error state
    }
  };

  return {
    initializingNodes,
    handleGetDefinition
  };
}
