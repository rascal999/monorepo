import { useState, useEffect } from 'react';

export function useNodeInteraction(onAddNode, onGetDefinition) {
  const [wasNodeClicked, setWasNodeClicked] = useState(false);
  const [lastCreatedNodeId, setLastCreatedNodeId] = useState(null);

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
    if (!node) return;

    // Ensure we have a valid source node with position
    const sourceNode = {
      ...node,
      position: node.position || { x: 0, y: 0 },
      data: {
        ...node.data,
        isLoading: true // Set loading state on parent node during creation
      }
    };
    
    // Preserve click state
    const prevWasNodeClicked = wasNodeClicked;
    setWasNodeClicked(false);
    
    // Create node (definition fetch is handled in the wrapped addNode)
    try {
      onAddNode(sourceNode, words.join(' '));
    } catch (error) {
      console.error('Error creating node:', error);
      sourceNode.data.isLoading = false; // Reset loading state on error
    }
    
    setWasNodeClicked(prevWasNodeClicked);
  };


  return {
    wasNodeClicked,
    handleNodeChange,
    handleNodeSelect,
    handleWordClick
  };
}
