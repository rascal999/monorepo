import { useState, useEffect } from 'react';

export function useNodeInteraction(onAddNode) {
  const [activeTab, setActiveTab] = useState('chat');
  const [wasNodeClicked, setWasNodeClicked] = useState(false);

  // Reset click state when node changes
  const handleNodeChange = (nodeId) => {
    setWasNodeClicked(false);
  };

  // Handle explicit node selection
  const handleNodeSelect = () => {
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
      
      onAddNode(sourceNode, words.join(' '), newPosition);
    }
  };

  return {
    activeTab,
    wasNodeClicked,
    setActiveTab,
    handleNodeChange,
    handleNodeSelect,
    handleWordClick
  };
}
