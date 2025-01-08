export function useNodeInteraction(onAddNode) {
  // Handle word click with proper async flow
  return {
    handleWordClick: async (node, words) => {
      console.log('useNodeInteraction.handleWordClick called with:', {
        nodeId: node?.id,
        nodePosition: node?.position,
        words
      });

      if (!node?.id || !node?.position || !words?.length) {
        console.log('useNodeInteraction.handleWordClick validation failed:', {
          hasNodeId: !!node?.id,
          hasPosition: !!node?.position,
          hasWords: !!words?.length
        });
        return;
      }

      console.log('useNodeInteraction calling onAddNode with:', {
        node: {
          id: node.id,
          position: node.position
        },
        term: words.join(' ')
      });

      try {
        // Wait for node creation to complete
        const newNodeId = await Promise.resolve(onAddNode(node, words.join(' ')));
        
        // Log result only if we got a valid node ID
        if (newNodeId) {
          console.log('useNodeInteraction.handleWordClick result:', { newNodeId });
          return { newNodeId };
        }
      } catch (error) {
        console.error('useNodeInteraction.handleWordClick error:', error);
      }
    }
  };
}
