import { useEffect, useRef, useCallback } from 'react';
import { chatService } from '../services/ai/chatService';
import { requestService } from '../services/ai/requestService';

export function useNodeDefinitionsBatch(activeGraph, onUpdateData) {
  // Simple state tracking
  const processedRef = useRef(new Set());

  // Clear processed nodes on graph change
  useEffect(() => {
    if (!activeGraph?.id) return;

    console.log('[NodeDefinitionsBatch] Graph changed:', {
      id: activeGraph.id,
      nodeCount: activeGraph.nodes?.length
    });

    // Clear processed nodes when graph changes
    processedRef.current.clear();
  }, [activeGraph?.id]);

  // Process nodes
  useEffect(() => {
    if (!activeGraph?.nodes?.length) return;

    // Find unprocessed nodes
    const unprocessedNodes = activeGraph.nodes.filter(n => !processedRef.current.has(n.id));
    console.log('[NodeDefinitionsBatch] Unprocessed nodes:', {
      graphId: activeGraph.id,
      total: activeGraph.nodes.length,
      unprocessed: unprocessedNodes.length,
      processed: processedRef.current.size
    });

    if (unprocessedNodes.length === 0) return;

    // Process first unprocessed node
    const node = unprocessedNodes[0];

    // Process node
    const processNode = async () => {
      if (!activeGraph?.id) return; // Verify graph still exists
      try {
        const nodeId = node.id;
        console.log('[NodeDefinitionsBatch] Processing node:', {
          id: nodeId,
          label: node.data.label,
          graphId: activeGraph.id
        });

        // Get definition
        const result = await chatService.getDefinition(
          node.data.label,
          activeGraph.title
        );

        // Verify node still exists
        const currentNode = activeGraph.nodes.find(n => n.id === nodeId);
        if (!currentNode) {
          console.error('[NodeDefinitionsBatch] Node no longer exists:', nodeId);
          return;
        }

        console.log('[NodeDefinitionsBatch] Got definition:', {
          id: nodeId,
          success: result.success,
          contentLength: result.message?.content?.length,
          graphId: activeGraph.id
        });

        // Update node
        if (result.success && result.message) {
          // Verify node data exists
          const nodeData = activeGraph.nodeData[nodeId] || {
            chat: [],
            notes: '',
            quiz: [],
            isLoadingDefinition: false
          };

          // Update with new chat data
          onUpdateData(nodeId, null, {
            ...nodeData,
            chat: [result.message],
            isLoadingDefinition: false
          }, true);

          processedRef.current.add(nodeId);
        }
      } catch (error) {
        console.error('[NodeDefinitionsBatch] Error:', {
          id: nodeId,
          error: error.message
        });
      }
    };

    processNode();
  }, [activeGraph?.id, activeGraph?.nodes]);

  return {};
}
