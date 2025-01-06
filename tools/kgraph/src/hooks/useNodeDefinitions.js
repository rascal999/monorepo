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
    console.log('Graph changed or cleared:', {
      prevGraphId,
      currentGraphId,
      hasGraph: !!activeGraph,
      initializingNodes: [...initializingNodes],
      loadingNodes: [...loadingNodes]
    });

    // Skip if this is the initial mount
    if (prevGraphId === undefined && currentGraphId === undefined) {
      setPrevGraphId(currentGraphId);
      return;
    }

    // Handle graph transitions
    if (currentGraphId !== prevGraphId) {
      console.log('Graph transition detected:', {
        from: prevGraphId,
        to: currentGraphId
      });

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

    console.log('Processing nodes for definitions:', {
      graphId: activeGraph.id,
      nodeCount: Object.keys(activeGraph.nodeData).length,
      initializingNodes: [...initializingNodes],
      loadingNodes: [...loadingNodes]
    });

    // Find nodes that need definitions
    const nodesToProcess = Object.entries(activeGraph.nodeData)
      .filter(([nodeId, data]) => {
        console.log('Checking node for processing:', {
          nodeId,
          hasChat: data.chat && data.chat.length > 0,
          isInitializing: initializingNodes.has(nodeId),
          isLoading: loadingNodes.has(nodeId),
          isLoadingDefinition: data.isLoadingDefinition
        });

        // Get the node from activeGraph
        const node = activeGraph.nodes.find(n => n.id === nodeId);
        if (!node) return false;

        // Skip if node already has chat data
        if (data.chat && data.chat.length > 0) {
          console.log('Node already has chat data:', nodeId);
          return false;
        }

        // Skip if node is being processed
        if (initializingNodes.has(nodeId) || loadingNodes.has(nodeId)) {
          console.log('Node is being processed:', nodeId);
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
    console.log('Processing nodes:', nodesToProcessNow.map(n => ({
      nodeId: n.id,
      label: n.data.label
    })));

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
            console.log('Node no longer exists:', node.id);
            setInitializingNodes(prev => {
              const next = new Set(prev);
              next.delete(node.id);
              return next;
            });
            return;
          }

          console.log('Definition callback received:', {
            nodeId: node.id,
            success: result.success
          });

          // Update chat data first
          if (result.success) {
            console.log('Definition received, updating node data:', {
              nodeId: node.id,
              message: result.message
            });
            // Ensure message is properly formatted
            const formattedMessage = {
              role: result.message.role || 'assistant',
              content: result.message.content
            };
            // Update chat data with definition
            onUpdateData(node.id, 'chat', [formattedMessage], true);
            // Clear loading states
            setInitializingNodes(prev => {
              const next = new Set(prev);
              next.delete(node.id);
              return next;
            });
          } else {
            // Update chat with error
            onUpdateData(node.id, 'chat', [{
              role: 'assistant',
              content: 'Error fetching definition. Please check your API key and try again.'
            }], true);
            // Clear loading states
            setInitializingNodes(prev => {
              const next = new Set(prev);
              next.delete(node.id);
              return next;
            });
          }

        }
      );
    });
  }, [activeGraph?.id, activeGraph?.nodes?.length]); // Re-run when graph changes or nodes are added

  const handleGetDefinition = (targetNode, graphId) => {
    if (!targetNode) return;
    
    // Skip if already loading
    if (initializingNodes.has(targetNode.id) || loadingNodes.has(targetNode.id)) {
      console.log('Definition request already in progress for node:', targetNode.id);
      return;
    }
    
    // Use provided graphId or fall back to activeGraph.id
    const effectiveGraphId = graphId || activeGraph?.id;
    if (!effectiveGraphId) {
      console.error('No graph ID available for definition request');
      return;
    }

    console.log('Starting definition request:', {
      nodeId: targetNode.id,
      graphId: effectiveGraphId
    });
    
    // Set loading state
    onUpdateData(targetNode.id, 'isLoadingDefinition', true);

    // Queue the definition request
    aiService.queueDefinitionRequest(
      targetNode.data.label,
      activeGraph.title,
      (result) => {
        console.log('Definition callback received:', {
          nodeId: targetNode.id,
          success: result.success
        });

          // Update chat data and clear loading state
          if (result.success) {
            const formattedMessage = {
              role: result.message.role || 'assistant',
              content: result.message.content
            };
            onUpdateData(targetNode.id, 'chat', [formattedMessage], true);
          } else {
            onUpdateData(targetNode.id, 'chat', [{
              role: 'assistant',
              content: 'Error fetching definition. Please check your API key and try again.'
            }], true);
          }
      }
    );
  };

  const handleSendMessage = async (node, nodeData, inputText) => {
    if (!node) return;

    const newMessage = { role: 'user', content: inputText };
    onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage]);
    setLoadingNodes(prev => new Set([...prev, node.id]));
    if (activeGraph?.id) {
      setNodeLoading(activeGraph.id, node.id, true);
    }

    try {
      const result = await aiService.getChatResponse([...(nodeData?.chat || []), newMessage], activeGraph.title);
      if (result.success) {
        onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage, result.message], true);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('OpenRouter API error:', error);
      onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage, {
        role: 'assistant',
        content: 'Error: Unable to get response. Please try again.'
      }], true); // Let wrapper handle selection
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
