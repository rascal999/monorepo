import { useState, useEffect } from 'react';

export function useNodeInteraction(onAddNode) {
  const [wasNodeClicked, setWasNodeClicked] = useState(false);

  // Track node changes and handle click state
  const handleNodeChange = (nodeId) => {
    console.log('useNodeInteraction handleNodeChange:', { nodeId });
    // Reset wasNodeClicked when node changes
    setWasNodeClicked(false);
  };

  // Handle explicit node selection
  const handleNodeSelect = () => {
    console.log('useNodeInteraction handleNodeSelect');
    // Only set wasNodeClicked if it's not already true
    setWasNodeClicked(true);
  };

  const handleWordClick = (node, words) => {
    if (node) {
      const sourceNode = {
        ...node,
        position: node.position || { x: 0, y: 0 }
      };
      
      // Let useNodeCreation handle positioning
      const prevWasNodeClicked = wasNodeClicked;
      setWasNodeClicked(false);
      
      onAddNode(sourceNode, words.join(' '));
      
      setWasNodeClicked(prevWasNodeClicked);
    }
  };

  return {
    wasNodeClicked,
    handleNodeChange,
    handleNodeSelect,
    handleWordClick
  };
}
