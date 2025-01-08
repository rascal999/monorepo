import { useState, useEffect } from 'react';
import { aiService } from '../services/ai';

export function useNodeDefinitionsBatch(activeGraph, onUpdateData) {
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

  return {
    initializingNodes
  };
}
