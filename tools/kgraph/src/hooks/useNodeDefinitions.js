import { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';

export function useNodeDefinitions(activeGraph, onUpdateData, setNodeLoading) {
  // Track nodes being loaded for chat responses
  const [loadingNodes, setLoadingNodes] = useState(new Set());
  // Track nodes being initialized
  const [initializingNodes, setInitializingNodes] = useState(new Set());

  // Process new nodes that need definitions in batches
  useEffect(() => {
    if (!activeGraph) return;

    // Find nodes that need definitions
    const nodesToProcess = Object.entries(activeGraph.nodeData)
      .filter(([nodeId, data]) => 
        (!data.chat || data.chat.length === 0) && // Needs definition
        !initializingNodes.has(nodeId) && // Not currently initializing
        !loadingNodes.has(nodeId) // Not currently loading
      )
      .map(([nodeId]) => activeGraph.nodes.find(n => n.id === nodeId))
      .filter(Boolean);

    if (nodesToProcess.length === 0) return;

    // Mark all nodes as initializing
    const newInitializing = new Set([...initializingNodes]);
    nodesToProcess.forEach(node => {
      newInitializing.add(node.id);
      setNodeLoading(activeGraph.id, node.id, true);
    });
    setInitializingNodes(newInitializing);

    // Queue each node for batch processing
    nodesToProcess.forEach(node => {
      aiService.queueDefinitionRequest(
        node.data.label,
        activeGraph.title,
        (result) => {
          if (result.success) {
            onUpdateData(node.id, 'chat', [result.message], true);
          } else {
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
          setNodeLoading(activeGraph.id, node.id, false);
        }
      );
    });
  }, [activeGraph?.nodeData, activeGraph?.id]);

  const handleGetDefinition = (targetNode) => {
    if (!targetNode) return;
    
    // Set loading state
    setInitializingNodes(prev => new Set([...prev, targetNode.id]));
    setNodeLoading(activeGraph.id, targetNode.id, true);

    // Queue the definition request
    aiService.queueDefinitionRequest(
      targetNode.data.label,
      activeGraph.title,
      (result) => {
        if (result.success) {
          onUpdateData(targetNode.id, 'chat', [result.message], true);
        } else {
          onUpdateData(targetNode.id, 'chat', [{
            role: 'assistant',
            content: 'Error fetching definition. Please check your API key and try again.'
          }], true);
        }
        // Clear loading states
        setInitializingNodes(prev => {
          const next = new Set(prev);
          next.delete(targetNode.id);
          return next;
        });
        setNodeLoading(activeGraph.id, targetNode.id, false);
      }
    );
  };

  const handleSendMessage = async (node, nodeData, inputText) => {
    if (!node) return;

    const newMessage = { role: 'user', content: inputText };
    onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage]);
    setLoadingNodes(prev => new Set([...prev, node.id]));
    setNodeLoading(activeGraph.id, node.id, true);

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
      setNodeLoading(activeGraph.id, node.id, false);
    }
  };

  return {
    initializingNodes,
    loadingNodes,
    handleGetDefinition,
    handleSendMessage
  };
}
