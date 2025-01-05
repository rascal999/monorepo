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
    if (activeGraph && activeGraph.lastSelectedNodeId) {
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      setSelectedNode(lastNode);
    } else {
      setSelectedNode(null);
    }
  }, [activeGraph]);

  const handleNodeClick = (node) => {
    // Ensure we have the complete node with position from the active graph
    const completeNode = activeGraph.nodes.find(n => n.id === node.id);
    setSelectedNode(completeNode);

    // Update the graph with new lastSelectedNodeId
    const updatedGraph = {
      ...activeGraph,
      lastSelectedNodeId: completeNode.id
    };
    updateGraph(updatedGraph);
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
