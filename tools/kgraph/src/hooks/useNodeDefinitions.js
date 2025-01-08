import { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';

export function useNodeDefinitions(activeGraph, onUpdateData) {
  // Track nodes being initialized
  const [initializingNodes, setInitializingNodes] = useState(new Set());

  // Track current graph ID to handle transitions
  const [prevGraphId, setPrevGraphId] = useState(activeGraph?.id);

  // Reset loading states when graph changes or is cleared
  useEffect(() => {
    const currentGraphId = activeGraph?.id;

    // Skip if this is the initial mount
    if (prevGraphId === undefined && currentGraphId === undefined) {
      setPrevGraphId(currentGraphId);
      return;
    }

    // Handle graph transitions
    if (currentGraphId !== prevGraphId) {
      // Clear initializing state and pending requests
      setInitializingNodes(new Set());
      aiService.clearStaleRequests();

      // If previous graph exists, clean up its state
      if (prevGraphId && activeGraph?.nodeData) {
        // Find and clean up any nodes marked as loading
        Object.entries(activeGraph.nodeData)
          .filter(([_, data]) => data.isLoadingDefinition)
          .forEach(([nodeId]) => {
            onUpdateData(nodeId, 'isLoadingDefinition', false);
          });
      }

      setPrevGraphId(currentGraphId);
    }
  }, [activeGraph?.id]);

  // Process new nodes that need definitions in batches
  useEffect(() => {
    if (!activeGraph) return;

    // Find nodes that need definitions
    const nodesToProcess = Object.entries(activeGraph.nodeData)
      .filter(([nodeId, data]) => {
        // Get the node from activeGraph
        const node = activeGraph.nodes.find(n => n.id === nodeId);
        if (!node) return false;

        // Skip if node already has chat data
        if (data.chat && data.chat.length > 0) {
          return false;
        }

        // Skip if node is being processed
        if (initializingNodes.has(nodeId)) {
          return false;
        }

        // Process node if it has no chat data
        return !data.chat || data.chat.length === 0;
      })
      .map(([nodeId]) => activeGraph.nodes.find(n => n.id === nodeId))
      .filter(Boolean);

    if (nodesToProcess.length === 0) return;

    // Process nodes in small batches to balance performance and reliability
    const nodesToProcessNow = nodesToProcess.slice(0, 3);

    // Process batch of nodes
    const processNodes = async () => {
      // Update loading states for all nodes in batch
      const newInitializingNodes = new Set(initializingNodes);
      nodesToProcessNow.forEach(node => {
        if (!newInitializingNodes.has(node.id)) {
          newInitializingNodes.add(node.id);
          onUpdateData(node.id, 'isLoadingDefinition', true);
        }
      });
      setInitializingNodes(newInitializingNodes);

      // Process nodes sequentially to avoid race conditions
      for (const node of nodesToProcessNow) {
        if (!activeGraph?.nodeData[node.id]) continue;
        await new Promise((resolve) => {
          aiService.queueDefinitionRequest(
            node.data.label,
            activeGraph.title,
            (result) => {
              // Skip if node no longer exists
              if (!activeGraph?.nodeData[node.id]) {
                setInitializingNodes(prev => {
                  const next = new Set(prev);
                  next.delete(node.id);
                  return next;
                });
                resolve();
                return;
              }

              // Update chat data and loading state in a single operation
              if (result.success) {
                // Ensure message is properly formatted
                const formattedMessage = {
                  role: result.message.role || 'assistant',
                  content: result.message.content
                };
                // Update chat data and loading state together
                onUpdateData(node.id, null, {
                  chat: [formattedMessage],
                  isLoadingDefinition: false
                }, true);
              } else {
                // Update chat with error and loading state together
                onUpdateData(node.id, null, {
                  chat: [{
                    role: 'assistant',
                    content: 'Error fetching definition. Please check your API key and try again.'
                  }],
                  isLoadingDefinition: false
                }, true);
              }

              // Clear initializing state
              setInitializingNodes(prev => {
                const next = new Set(prev);
                next.delete(node.id);
                return next;
              });

              resolve();
            }
          );
        });
      }
    };

    processNodes().catch(error => {
      console.error('Error processing nodes:', error);
    });
  }, [activeGraph?.id, activeGraph?.nodes?.length]); // Re-run when graph changes or nodes are added

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

            // Signal completion
            resolve();
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
