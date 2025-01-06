import { useState, useEffect } from 'react';

export function useNodeSelection(activeGraph, updateGraph) {
  const [selectedNode, setSelectedNode] = useState(() => {
    if (activeGraph && activeGraph.lastSelectedNodeId) {
      return activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
    }
    return null;
  });

  // Update selected node when switching graphs
  useEffect(() => {
    if (activeGraph) {
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      if (lastNode) {
        setSelectedNode(lastNode);
      } else {
        setSelectedNode(null);
      }
    } else {
      setSelectedNode(null);
    }
  }, [activeGraph?.id]); // Only update when switching graphs

  const handleNodeClick = (node, isUserClick = true) => {
    console.log('useNodeSelection handleNodeClick:', { node, isUserClick, activeGraph });
    
    if (!node || !isUserClick || !activeGraph) return;
    
    // Only allow selecting nodes that have required data
    if (!node.data?.label) {
      console.warn('useNodeSelection: Ignoring invalid node', { node });
      return;
    }

    // Update selection
    setSelectedNode(node);
    
    // Update graph selection state
    updateGraph({
      ...activeGraph,
      lastSelectedNodeId: node.id
    });
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
