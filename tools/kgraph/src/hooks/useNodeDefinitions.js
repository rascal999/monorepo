import { useState, useEffect } from 'react';
import { fetchChatCompletion } from '../services/openRouterApi';

export function useNodeDefinitions(activeGraph, onUpdateData, setNodeLoading) {
  // Track nodes being loaded for chat responses
  const [loadingNodes, setLoadingNodes] = useState(new Set());
  // Track nodes being initialized
  const [initializingNodes, setInitializingNodes] = useState(new Set());

  // Process new nodes that need definitions
  useEffect(() => {
    if (!activeGraph) return;

    // Find nodes that need definitions
    const nodesToProcess = Object.entries(activeGraph.nodeData)
      .filter(([nodeId, data]) => 
        data.chat === null && // Needs definition
        !initializingNodes.has(nodeId) && // Not currently initializing
        !loadingNodes.has(nodeId) // Not currently loading
      )
      .map(([nodeId]) => activeGraph.nodes.find(n => n.id === nodeId))
      .filter(Boolean);

    if (nodesToProcess.length === 0) return;

    // Process nodes sequentially
    let currentIndex = 0;
    let timeoutId = null;

    const processNextNode = () => {
      if (currentIndex >= nodesToProcess.length) return;
      
      const node = nodesToProcess[currentIndex];
      handleGetDefinition(node, false); // Pass isUserClick=false
      currentIndex++;
      
      // Schedule next node with delay
      if (currentIndex < nodesToProcess.length) {
        timeoutId = setTimeout(processNextNode, 1000);
      }
    };

    // Start processing after initial delay
    timeoutId = setTimeout(processNextNode, 500);

    // Cleanup function
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [activeGraph?.nodeData, activeGraph?.id]); // Also track graph ID changes

  const handleGetDefinition = async (targetNode, isUserClick = false) => {
    if (!targetNode) return;
    
    try {
      // Set initializing and loading states
      setInitializingNodes(prev => new Set([...prev, targetNode.id]));
      setNodeLoading(activeGraph.id, targetNode.id, true);

      const messages = [
        { 
          role: 'system', 
          content: `Define ${targetNode.data.label} in the context of ${activeGraph.title}. Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. No parentheses around terms. Total response must be under 120 words.` 
        }
      ];
      
      const aiMessage = await fetchChatCompletion(messages);
      onUpdateData(targetNode.id, 'chat', [aiMessage], true); // Let wrapper handle selection
    } catch (error) {
      console.error('OpenRouter API error:', error);
      onUpdateData(targetNode.id, 'chat', [{
        role: 'assistant',
        content: 'Error fetching definition. Please check your API key and try again.'
      }], true); // Let wrapper handle selection
    } finally {
      // Clear initializing and loading states
      setInitializingNodes(prev => {
        const next = new Set(prev);
        next.delete(targetNode.id);
        return next;
      });
      setNodeLoading(activeGraph.id, targetNode.id, false);
    }
  };

  const handleSendMessage = async (node, nodeData, inputText) => {
    if (!node) return;

    const newMessage = { role: 'user', content: inputText };
    onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage]);
    setLoadingNodes(prev => new Set([...prev, node.id]));
    setNodeLoading(activeGraph.id, node.id, true);

    try {
      const messages = [
        { 
          role: 'system', 
          content: `Define ${node.data.label} in the context of ${activeGraph.title}. Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. No parentheses around terms. Total response must be under 120 words.` 
        },
        ...(nodeData?.chat || []),
        newMessage
      ];
      
      const aiMessage = await fetchChatCompletion(messages);
      onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage, aiMessage], true); // Let wrapper handle selection
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
