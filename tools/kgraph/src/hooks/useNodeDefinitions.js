import { useCallback, useEffect, useRef } from 'react';
import { useNodeDefinitionsBatch } from './useNodeDefinitionsBatch';
import { chatService } from '../services/ai/chatService';

export function useNodeDefinitions(activeGraph, onUpdateData) {
  // Track active graph
  const activeGraphRef = useRef(null);

  // Debug current graph state
  useEffect(() => {
    console.log('[NodeDefinitions] Current graph state:', {
      hasGraph: Boolean(activeGraph),
      nodeCount: activeGraph?.nodes?.length,
      nodeDataCount: Object.keys(activeGraph?.nodeData || {}).length,
      prevGraphId: activeGraphRef.current?.id
    });

    // Update active graph ref
    if (activeGraph?.id !== activeGraphRef.current?.id) {
      activeGraphRef.current = activeGraph;
    }
  }, [activeGraph]);

  // Use batch hook for automatic definition fetching
  const { initializingNodes } = useNodeDefinitionsBatch(activeGraph, onUpdateData);

  // Create handleSendMessage for chat interactions
  const handleSendMessage = useCallback(async (nodeId, content, onStream) => {
    if (!nodeId || !activeGraph) {
      console.error('[NodeDefinitions] Invalid node ID or missing graph:', {
        nodeId,
        hasGraph: !!activeGraph,
        activeGraphId: activeGraph?.id
      });
      return;
    }

    // Verify node exists
    const node = activeGraph.nodes.find(n => n.id === nodeId);
    if (!node) {
      console.error('[NodeDefinitions] Node not found:', nodeId);
      return;
    }

    console.log('[NodeDefinitions] Sending message:', {
      nodeId,
      contentLength: content?.length,
      hasChat: Boolean(activeGraph.nodeData[nodeId]?.chat),
      chatLength: activeGraph.nodeData[nodeId]?.chat?.length,
      nodeLabel: node.data.label
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

      console.log('[NodeDefinitions] Got response:', {
        nodeId,
        success: result.success,
        hasMessage: Boolean(result.message),
        messageLength: result.message?.content?.length
      });

      if (!result.success) {
        throw new Error(result.error || 'Failed to get chat response');
      }

      // Verify graph is still active
      if (activeGraph.id !== activeGraphRef.current?.id) {
        console.warn('[NodeDefinitions] Graph changed during request');
        return;
      }

      // Update chat with response
      if (!onStream) {
        onUpdateData(nodeId, null, {
          chat: [...messages, result.message]
        });
      }
    } catch (error) {
      console.error('[NodeDefinitions] Error sending message:', error);
      throw error;
    }
  }, [activeGraph, onUpdateData]);

  return {
    initializingNodes,
    handleSendMessage
  };
}
