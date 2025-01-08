import { useState, useEffect, useRef } from 'react';
import { chatService } from '../services/ai/chatService';
import { requestService } from '../services/ai/requestService';

export function useNodeDefinitionsBatch(activeGraph, onUpdateData) {
  // Track nodes being initialized
  const [initializingNodes, setInitializingNodes] = useState(new Set());
  
  // Track nodes that were manually initialized
  const manuallyInitializedRef = useRef(new Set());

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
      console.log('useNodeDefinitionsBatch: Graph changed, cleaning up states:', {
        prevId: prevGraphId,
        currentId: currentGraphId
      });

      // Clear initializing state and pending requests
      setInitializingNodes(new Set());
      manuallyInitializedRef.current.clear();
      requestService.clearStaleRequests();

      // If previous graph exists, clean up its state
      if (prevGraphId && activeGraph?.nodeData) {
        // Find and clean up any nodes marked as loading
        Object.entries(activeGraph.nodeData)
          .filter(([_, data]) => data.isLoadingDefinition)
          .forEach(([nodeId]) => {
            console.log('useNodeDefinitionsBatch: Clearing loading state for node:', nodeId);
            onUpdateData(nodeId, null, {
              chat: activeGraph.nodeData[nodeId]?.chat || [],
              isLoadingDefinition: false
            });
          });
      }

      setPrevGraphId(currentGraphId);
    }
  }, [activeGraph?.id, onUpdateData, prevGraphId]);

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

        // Skip if node was manually initialized
        if (manuallyInitializedRef.current.has(nodeId)) {
          return false;
        }

        // Process node if it has no chat data
        return !data.chat || data.chat.length === 0;
      })
      .map(([nodeId]) => activeGraph.nodes.find(n => n.id === nodeId))
      .filter(Boolean);

    if (nodesToProcess.length === 0) return;

    console.log('useNodeDefinitionsBatch: Processing nodes:', {
      count: nodesToProcess.length,
      nodes: nodesToProcess.map(n => ({ id: n.id, label: n.data.label }))
    });

    // Process nodes in small batches to balance performance and reliability
    const nodesToProcessNow = nodesToProcess.slice(0, 3);

    // Process batch of nodes
    const processNodes = async () => {
      // Initialize chat arrays and set loading states for all nodes in batch
      const newInitializingNodes = new Set(initializingNodes);
      nodesToProcessNow.forEach(node => {
        if (!newInitializingNodes.has(node.id)) {
          newInitializingNodes.add(node.id);
          // Initialize chat array and set loading state
          onUpdateData(node.id, null, {
            chat: [],
            isLoadingDefinition: true
          });
        }
      });
      setInitializingNodes(newInitializingNodes);

      // Process nodes sequentially to avoid race conditions
      for (const node of nodesToProcessNow) {
        if (!activeGraph?.nodeData[node.id]) continue;
        try {
          console.log('useNodeDefinitionsBatch: Fetching definition for node:', {
            id: node.id,
            label: node.data.label
          });

          // Get definition using chatService
          const result = await chatService.getDefinition(
            node.data.label,
            activeGraph.title
          );

          // Skip if node no longer exists
          if (!activeGraph?.nodeData[node.id]) {
            console.log('useNodeDefinitionsBatch: Node no longer exists:', node.id);
            continue;
          }

          try {
            // Update chat data - loading state will be cleared by useNodeData
            if (result.success && result.message) {
              onUpdateData(node.id, null, {
                chat: [result.message],
                isLoadingDefinition: false
              }, true);
            } else {
              throw new Error(result.error || 'Definition request failed');
            }
          } finally {
            // Always clean up initializing state
            setInitializingNodes(prev => {
              const next = new Set(prev);
              next.delete(node.id);
              return next;
            });
          }
        } catch (error) {
          console.error('useNodeDefinitionsBatch: Error processing node:', error);
          // Ensure loading state is cleared and error message is shown
          onUpdateData(node.id, null, {
            chat: [{
              role: 'assistant',
              content: 'Error fetching definition. Please try again.'
            }],
            isLoadingDefinition: false
          });
          setInitializingNodes(prev => {
            const next = new Set(prev);
            next.delete(node.id);
            return next;
          });
        }
      }
    };

    processNodes().catch(error => {
      console.error('useNodeDefinitionsBatch: Error processing nodes:', error);
      // Clean up any remaining nodes
      nodesToProcessNow.forEach(node => {
        onUpdateData(node.id, null, {
          chat: [{
            role: 'assistant',
            content: 'Error fetching definition. Please try again.'
          }],
          isLoadingDefinition: false
        });
        setInitializingNodes(prev => {
          const next = new Set(prev);
          next.delete(node.id);
          return next;
        });
      });
    });
  }, [activeGraph, onUpdateData, initializingNodes]); // Re-run when graph or onUpdateData changes

  return {
    initializingNodes
  };
}
