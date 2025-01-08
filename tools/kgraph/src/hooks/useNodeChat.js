import { useState } from 'react';
import { aiService } from '../services/aiService';

export function useNodeChat(activeGraph, onUpdateData, setNodeLoading) {
  // Track nodes being loaded for chat responses
  const [loadingNodes, setLoadingNodes] = useState(new Set());

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
    loadingNodes,
    handleSendMessage
  };
}
