export function useNodeInteraction(onAddNode) {
  // Simple pass-through to add node with minimal validation
  return {
    handleWordClick: (node, words) => {
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

      const newNodeId = onAddNode(node, words.join(' '));
      console.log('useNodeInteraction.handleWordClick result:', { newNodeId });
    }
  };
}
