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
    console.log('[NodePosition] updateNodePosition called:', {
      hasUpdate: !!update,
      updateType: update?.nodes ? 'full-graph' : 'single-node',
      graphId: activeGraph?.id,
      stack: new Error().stack
    });

    if (!activeGraph) {
      console.warn('[NodePosition] Called without activeGraph');
      return;
    }
    if (!update) {
      console.warn('[NodePosition] Called without update data');
      return;
    }
    if (typeof updateGraph !== 'function') {
      console.error('[NodePosition] updateGraph is not a function');
      return;
    }

    // Handle full graph update
    if (update.nodes) {
      console.log('[NodePosition] Handling full graph update');
      updateGraph(update);
      return;
    }

    // Handle single node position update
    const nodeToUpdate = activeGraph.nodes?.find(node => node.id === update.id);
    if (!nodeToUpdate) {
      console.warn('[NodePosition] Node not found:', update.id);
      return;
    }

    console.log('[NodePosition] Updating node position:', {
      nodeId: nodeToUpdate.id,
      oldPosition: nodeToUpdate.position,
      newPosition: update.position
    });

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
