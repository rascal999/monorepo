import { useCallback } from 'react';
import { useNodeDefinitionsBatch } from './useNodeDefinitionsBatch';
import { chatService } from '../services/ai/chatService';

export function useNodeDefinitions(activeGraph, onUpdateData) {
  // Use batch hook for automatic definition fetching
  const { initializingNodes } = useNodeDefinitionsBatch(activeGraph, onUpdateData);

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
      // Get current chat messages
      const currentChat = activeGraph.nodeData[nodeId]?.chat || [];
      
      // Add user message
      const userMessage = { role: 'user', content };
      const messages = [...currentChat, userMessage];

      // Get response from chatService
      const result = await chatService.getChatResponse(
        messages,
        activeGraph.title,
        onStream,
        false // Not a definition request
      );

      if (!result.success) {
        throw new Error(result.error || 'Failed to get chat response');
      }

      // Update chat with response
      if (!onStream) {
        onUpdateData(nodeId, null, {
          chat: [...messages, result.message]
        });
      }
    } catch (error) {
      console.error('useNodeDefinitions: Error sending chat message:', error);
      throw error;
    }
  }, [activeGraph, onUpdateData]);

  return {
    initializingNodes,
    handleSendMessage
  };
}
