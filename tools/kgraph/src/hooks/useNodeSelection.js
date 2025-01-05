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
    console.log('useNodeSelection handleNodeClick:', { node });
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
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
