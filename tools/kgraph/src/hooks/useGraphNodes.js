import { useState, useEffect } from 'react';

export function useGraphNodes(graph, isDragging, draggedNodeId) {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    if (!graph) {
      setNodes([]);
      return;
    }

    // Validate input
    if (!graph || !Array.isArray(graph.nodes)) {
      console.error('Invalid graph:', graph);
      return;
    }

    try {
      // Create a map of current positions - preserve exact references
      const currentPositions = {};
      graph.nodes.forEach(node => {
        if (node.position) {
          currentPositions[node.id] = node.position; // Keep original reference
        }
      });

      // Track processed node IDs to prevent duplicates
      const processedIds = new Set();

      // Process nodes with validation
      const processedNodes = graph.nodes.reduce((acc, node) => {
        // Skip duplicate nodes
        if (!node || !node.id || processedIds.has(node.id)) {
          return acc;
        }
        processedIds.add(node.id);

        // Determine node position with validation
        let position;
        
        if (isDragging && node.id === draggedNodeId) {
          // Use current position for dragged node
          position = currentPositions[node.id] || node.position;
        } else if (currentPositions[node.id]) {
          // Use existing position from current state
          position = currentPositions[node.id];
        } else if (node.position?.x !== undefined && node.position?.y !== undefined) {
          // Use provided position if valid
          position = node.position;
        } else {
          // Fallback to default position
          position = { x: 0, y: 0 };
          console.warn('No valid position found for node:', node.id);
        }

        // Add classes for styling
        const classes = [];
        if (node.id === graph.lastSelectedNodeId) {
          classes.push('selected');
        }
        if (node.data?.isLoading) {
          classes.push('loading');
        }

        acc.push({
          id: node.id,
          position,
          data: { 
            ...node.data,
            label: node.data?.label || 'Untitled'
          },
          classes: classes.join(' ')
        });
        return acc;
      }, []);

      setNodes(processedNodes);
    } catch (error) {
      console.error('Error updating nodes:', error);
    }
  }, [graph, isDragging, draggedNodeId]);

  return { nodes };
}
