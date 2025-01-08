import { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';

export function useNodeDefinitions(activeGraph, onUpdateData, setNodeLoading) {
  // Track nodes being loaded for chat responses
  const [loadingNodes, setLoadingNodes] = useState(new Set());
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
      // First clear all loading states
      setInitializingNodes(new Set());
      setLoadingNodes(new Set());

      // Clear any pending requests in AIService
      aiService.clearStaleRequests();

      // If previous graph exists, clean up its state
      if (prevGraphId) {
        // Find all nodes that were being loaded
        const nodesToCleanup = new Set([
          ...initializingNodes,
          ...loadingNodes,
          // Also include any nodes marked as loading in nodeData
          ...(activeGraph?.nodeData ? 
            Object.entries(activeGraph.nodeData)
              .filter(([_, data]) => data.isLoadingDefinition)
              .map(([id]) => id) : 
            []
          )
        ]);

        // Clean up each node's state
        nodesToCleanup.forEach(nodeId => {
          onUpdateData(nodeId, 'isLoadingDefinition', false);
          if (activeGraph?.id) {
            setNodeLoading(activeGraph.id, nodeId, false);
          }
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
        if (initializingNodes.has(nodeId) || loadingNodes.has(nodeId)) {
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

    // Update loading states for all nodes in batch
    const newInitializingNodes = new Set(initializingNodes);
    nodesToProcessNow.forEach(node => {
      newInitializingNodes.add(node.id);
      onUpdateData(node.id, 'isLoadingDefinition', true);
    });
    setInitializingNodes(newInitializingNodes);

    // Process batch of nodes
    nodesToProcessNow.forEach(node => {
      aiService.queueDefinitionRequest(
        node.data.label,
        activeGraph.title,
        (result) => {
          // Ensure the node and graph still exist
          if (!activeGraph?.nodeData[node.id]) {
            setInitializingNodes(prev => {
              const next = new Set(prev);
              next.delete(node.id);
              return next;
            });
            return;
          }

          // Update chat data first
          if (result.success) {
            // Ensure message is properly formatted
            const formattedMessage = {
              role: result.message.role || 'assistant',
              content: result.message.content
            };
            // Update chat data with definition
            onUpdateData(node.id, 'chat', [formattedMessage], true);
          } else {
            // Update chat with error
            onUpdateData(node.id, 'chat', [{
              role: 'assistant',
              content: 'Error fetching definition. Please check your API key and try again.'
            }], true);
          }
          
          // Clear loading states
          setInitializingNodes(prev => {
            const next = new Set(prev);
            next.delete(node.id);
            return next;
          });

        }
      );
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
    
    // Skip if already loading
    if (initializingNodes.has(targetNode.id) || loadingNodes.has(targetNode.id)) {
      console.log('Node already loading:', targetNode.id);
      return;
    }
    
    // Use provided graphId or fall back to activeGraph.id
    const effectiveGraphId = graphId || activeGraph?.id;
    if (!effectiveGraphId) {
      console.error('No graph ID available for definition request');
      return;
    }

    try {
      // Set loading state
      console.log('Setting loading state for node:', targetNode.id);
      onUpdateData(targetNode.id, 'isLoadingDefinition', true);
      setInitializingNodes(prev => new Set([...prev, targetNode.id]));

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
                // Update chat data and mark node as complete
              onUpdateData(targetNode.id, 'chat', [formattedMessage], true);
              onUpdateData(targetNode.id, 'isLoadingDefinition', false);
              } else {
              // Update chat with error and mark node as complete
              onUpdateData(targetNode.id, 'chat', [{
                role: 'assistant',
                content: 'Error fetching definition. Please check your API key and try again.'
              }], true);
              onUpdateData(targetNode.id, 'isLoadingDefinition', false);
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

  const handleSendMessage = async (node, nodeData, inputText, onStream) => {
    if (!node) return;

    const newMessage = { role: 'user', content: inputText };
    const currentChat = [...(nodeData?.chat || []), newMessage];
    onUpdateData(node.id, 'chat', currentChat);
    
    setLoadingNodes(prev => new Set([...prev, node.id]));
    if (activeGraph?.id) {
      setNodeLoading(activeGraph.id, node.id, true);
    }

    try {
      const result = await aiService.getChatResponse(
        currentChat,
        activeGraph.title,
        onStream ? (update) => {
          if (update.success) {
            onStream(update);
          }
        } : null
      );

      if (result.success) {
        onUpdateData(node.id, 'chat', [...currentChat, result.message], true);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('OpenRouter API error:', error);
      onUpdateData(node.id, 'chat', [...currentChat, {
        role: 'assistant',
        content: 'Error: Unable to get response. Please try again.'
      }], true);
    } finally {
      setLoadingNodes(prev => {
        const next = new Set(prev);
        next.delete(node.id);
        return next;
      });
      if (activeGraph?.id) {
        setNodeLoading(activeGraph.id, node.id, false);
      }
    }
  };

  return {
    initializingNodes,
    loadingNodes,
    handleGetDefinition,
    handleSendMessage
  };
}
