import { useState, useEffect } from 'react';

export function useNodeSelection(activeGraph, updateGraph) {
  const [selectedNode, setSelectedNode] = useState(null);

  // Track whether a node was manually selected
  const [hasManualSelection, setHasManualSelection] = useState(false);

  // Handle initial node selection and graph changes
  useEffect(() => {
    console.log('[NodeSelection] Selection effect:', {
      hasActiveGraph: !!activeGraph,
      lastSelectedNodeId: activeGraph?.lastSelectedNodeId,
      hasNodes: activeGraph?.nodes?.length,
      hasManualSelection,
      stack: new Error().stack
    });

    // Always clear selection when switching graphs
    if (!activeGraph) {
      console.log('[NodeSelection] No active graph, clearing selection');
      setSelectedNode(null);
      setHasManualSelection(false);
      return;
    }

    // Reset manual selection flag when switching graphs
    setHasManualSelection(false);

    // Try to find node with chat data first
    const nodeWithChat = activeGraph.nodes.find(n => 
      activeGraph.nodeData[n.id]?.chat?.length > 0
    );

    // Use node with chat, lastSelectedNode, or first node
    const nodeToSelect = nodeWithChat || 
      (activeGraph.lastSelectedNodeId && 
        activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId)) ||
      activeGraph.nodes[0];

    if (nodeToSelect) {
      console.log('[NodeSelection] Selecting node:', {
        nodeId: nodeToSelect.id,
        hasChat: !!activeGraph.nodeData[nodeToSelect.id]?.chat?.length,
        isLastSelected: nodeToSelect.id === activeGraph.lastSelectedNodeId
      });
      setSelectedNode(nodeToSelect);
      
      // Update graph selection state if needed
      if (activeGraph.lastSelectedNodeId !== nodeToSelect.id) {
        updateGraph({
          ...activeGraph,
          lastSelectedNodeId: nodeToSelect.id
        });
      }
    } else {
      console.log('[NodeSelection] No node to select, clearing selection');
      setSelectedNode(null);
    }
  }, [activeGraph?.id]); // Only run on graph changes

  const handleNodeClick = (node, isUserClick = true) => {
    console.log('useNodeSelection handleNodeClick:', { node, isUserClick, activeGraph });
    
    if (!node || !isUserClick || !activeGraph) return;
    
    // Only allow selecting nodes that have required data
    if (!node.data?.label) {
      console.warn('useNodeSelection: Ignoring invalid node', { node });
      return;
    }

    console.log('[NodeSelection] Manual node selection:', {
      nodeId: node.id,
      nodeLabel: node.data?.label
    });

    // Mark as manually selected
    setHasManualSelection(true);
    
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
