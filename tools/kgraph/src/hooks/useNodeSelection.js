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

    // Reset manual selection flag when switching graphs
    setHasManualSelection(false);

    // Handle node selection
    if (!hasManualSelection) {
      if (!activeGraph) {
        console.log('[NodeSelection] No active graph, clearing selection');
        setSelectedNode(null);
        return;
      }

      // Try to find the last selected node
      const lastNode = activeGraph.lastSelectedNodeId 
        ? activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId)
        : null;

      console.log('[NodeSelection] Finding node to select:', {
        lastSelectedNodeId: activeGraph.lastSelectedNodeId,
        foundLastNode: !!lastNode,
        lastNodeLabel: lastNode?.data?.label
      });

      // If no last selected node or not found, use first node
      const nodeToSelect = lastNode || activeGraph.nodes[0];

      if (nodeToSelect) {
        console.log('[NodeSelection] Auto-selecting node:', {
          nodeId: nodeToSelect.id,
          nodeLabel: nodeToSelect.data?.label,
          isLastSelected: nodeToSelect === lastNode
        });
        setSelectedNode(nodeToSelect);
        
        // Ensure lastSelectedNodeId is set in graph
        if (activeGraph.lastSelectedNodeId !== nodeToSelect.id) {
          console.log('[NodeSelection] Updating graph lastSelectedNodeId:', nodeToSelect.id);
          updateGraph({
            ...activeGraph,
            lastSelectedNodeId: nodeToSelect.id
          });
        }
      } else {
        console.log('[NodeSelection] No node to select, clearing selection');
        setSelectedNode(null);
      }
    }
  }, [activeGraph?.id]); // Only run on graph changes, not lastSelectedNodeId changes

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
