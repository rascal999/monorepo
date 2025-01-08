import { useEffect, useCallback } from 'react';

export function useNodePosition(activeGraph, updateGraph) {
  // Validate inputs
  useEffect(() => {
    if (!activeGraph || typeof updateGraph !== 'function') {
      console.error('[NodePosition] Invalid inputs:', {
        hasActiveGraph: !!activeGraph,
        updateGraphType: typeof updateGraph
      });
    }
  }, [activeGraph, updateGraph]);

  const updateNodePosition = useCallback((update) => {
    // Basic validation
    if (!activeGraph || !update || typeof updateGraph !== 'function') {
      console.warn('[NodePosition] Invalid inputs:', {
        hasActiveGraph: !!activeGraph,
        hasUpdate: !!update,
        updateGraphType: typeof updateGraph
      });
      return;
    }

    // Handle full graph update
    if (update.nodes) {
      // Only update if positions actually changed
      const hasPositionChanges = update.nodes.some((newNode, i) => {
        const oldNode = activeGraph.nodes[i];
        return oldNode && (
          oldNode.position.x !== newNode.position.x ||
          oldNode.position.y !== newNode.position.y
        );
      });

      if (hasPositionChanges) {
        updateGraph(update);
      }
      return;
    }

    // Handle single node position update
    const nodeToUpdate = activeGraph.nodes?.find(node => node.id === update.id);
    if (!nodeToUpdate) {
      console.warn('[NodePosition] Node not found:', update.id);
      return;
    }

    // Only update if position actually changed
    if (nodeToUpdate.position.x === update.position.x && 
        nodeToUpdate.position.y === update.position.y) {
      return;
    }

    // Create updated graph with new position
    const updatedGraph = {
      ...activeGraph,
      nodes: activeGraph.nodes.map(node => 
        node.id === update.id 
          ? { ...nodeToUpdate, position: update.position }
          : node
      )
    };

    // Pass the node ID to indicate this is a position update
    updateGraph(updatedGraph, update.id);
  }, [activeGraph, updateGraph]);

  return { updateNodePosition };
}
