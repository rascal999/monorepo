import { useState, useEffect, useRef } from 'react';

export function useNodeSelection(activeGraph, updateGraph, graphs) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [prevGraphId, setPrevGraphId] = useState(null);
  const lastManualNodeRef = useRef(null);

  // Handle graph changes and selection restoration
  useEffect(() => {
    // Clear selection when no active graph
    if (!activeGraph) {
      setSelectedNode(null);
      setPrevGraphId(null);
      lastManualNodeRef.current = null;
      return;
    }

    // Check if actually switching graphs
    const isGraphSwitch = prevGraphId !== activeGraph.id;

    // If switching graphs and we have a previous selection
    if (isGraphSwitch && prevGraphId && selectedNode) {
      // Find the previous graph
      const prevGraph = graphs?.find(g => g.id === parseInt(prevGraphId));
      if (prevGraph) {
        // Update the previous graph's lastSelectedNodeId
        updateGraph({
          ...prevGraph,
          lastSelectedNodeId: selectedNode.id
        });
      }
    }
    
    setPrevGraphId(activeGraph.id);

    // Try to restore the last selected node
    if (activeGraph.lastSelectedNodeId) {
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      if (lastNode) {
        setSelectedNode(lastNode);
        return;
      }
    }

    // If no last selected node or it's not found, use priority selection
    const nodeWithChat = activeGraph.nodes.find(n => {
      return !!activeGraph.nodeData[n.id]?.chat?.length;
    });

    const nodeToSelect = nodeWithChat || activeGraph.nodes[0];

    if (nodeToSelect) {
      setSelectedNode(nodeToSelect);
      
      // Update graph selection state
      if (activeGraph.lastSelectedNodeId !== nodeToSelect.id) {
        updateGraph({
          ...activeGraph,
          lastSelectedNodeId: nodeToSelect.id
        });
      }
    } else {
      setSelectedNode(null);
    }
  }, [activeGraph?.id]); // Only run on graph changes

  const handleNodeClick = (node, isUserClick = true) => {
    if (!node || !isUserClick || !activeGraph) {
      return;
    }
    
    // Only allow selecting nodes that have required data
    if (!node.data?.label) {
      console.warn('Ignoring invalid node:', { node });
      return;
    }
    
    // Store manual selection
    lastManualNodeRef.current = node;
    
    // Update selection
    setSelectedNode(node);
    
    // Update graph selection state
    if (activeGraph.lastSelectedNodeId !== node.id) {
      updateGraph({
        ...activeGraph,
        lastSelectedNodeId: node.id
      });
    }
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
