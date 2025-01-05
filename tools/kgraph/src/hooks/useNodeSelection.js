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
    console.log('useNodeSelection handleNodeClick:', { node, isUserClick });
    if (node && isUserClick) { // Only handle explicit user clicks
      // Ensure we have the complete node with position from the active graph
      const completeNode = activeGraph.nodes.find(n => n.id === node.id);
      console.log('useNodeSelection found completeNode:', { completeNode });
      setSelectedNode(completeNode);
      console.log('useNodeSelection after setSelectedNode');

      // Update the graph with new lastSelectedNodeId
      const updatedGraph = {
        ...activeGraph,
        lastSelectedNodeId: completeNode.id
      };
      console.log('useNodeSelection updating graph with:', { updatedGraph });
      updateGraph(updatedGraph);
    }
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
