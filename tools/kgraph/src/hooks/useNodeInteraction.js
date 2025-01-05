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
      // Calculate new node position relative to source node
      // Position new node below and slightly to the right of source node
      const sourcePosition = node.position || { x: 0, y: 0 };
      const newPosition = {
        x: sourcePosition.x + 150, // Offset horizontally by 150px
        y: sourcePosition.y + 100  // Offset vertically by 100px
      };
      
      const sourceNode = {
        ...node,
        position: sourcePosition
      };
      
      // Prevent wasNodeClicked from being set to true during word click node creation
      const prevWasNodeClicked = wasNodeClicked;
      setWasNodeClicked(false);
      
      onAddNode(sourceNode, words.join(' '), newPosition);
      
      // Restore previous wasNodeClicked state
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
