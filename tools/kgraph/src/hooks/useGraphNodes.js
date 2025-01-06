import { useState, useCallback } from 'react';

export function useGraphNodes(graph, isDragging, draggedNodeId) {
  const [nodes, setNodes] = useState([]);

  const updateNodes = useCallback((graph, existingNodes) => {
    if (!graph) {
      setNodes([]);
      return;
    }

    // Validate input
    if (!Array.isArray(graph.nodes) || !Array.isArray(existingNodes)) {
      console.error('Invalid graph or existingNodes:', { graph, existingNodes });
      return;
    }

    try {
      console.log('useGraphNodes.updateNodes called with:', {
        graphId: graph.id,
        nodeCount: graph.nodes.length,
        existingNodeCount: existingNodes.length
      });

      // Create a map of current positions
      const currentPositions = {};
      nodes.forEach(node => {
        if (node.position) {
          currentPositions[node.id] = { ...node.position };
        }
      });

      console.log('Current node positions:', currentPositions);

      // Track processed node IDs to prevent duplicates
      const processedIds = new Set();

      // Process nodes with validation
      const processedNodes = graph.nodes.reduce((acc, node) => {
        // Skip duplicate nodes
        if (!node || !node.id || processedIds.has(node.id)) {
          return acc;
        }
        processedIds.add(node.id);

        console.log('Processing node:', {
          nodeId: node.id,
          hasPosition: !!node.position,
          position: node.position,
          isDragging,
          isDraggedNode: node.id === draggedNodeId,
          hasCurrentPosition: !!currentPositions[node.id],
          data: node.data
        });

        // Determine node position with validation
        let position;
        
        if (isDragging && node.id === draggedNodeId) {
          // Use current position for dragged node
          position = currentPositions[node.id] || node.position;
          console.log('Using drag position for node:', {
            nodeId: node.id,
            position
          });
        } else if (currentPositions[node.id]) {
          // Use existing position from current state
          position = currentPositions[node.id];
          console.log('Using existing position for node:', {
            nodeId: node.id,
            position
          });
        } else if (node.position?.x !== undefined && node.position?.y !== undefined) {
          // Use provided position if valid
          position = { ...node.position };
          console.log('Using provided position for node:', {
            nodeId: node.id,
            position
          });
        } else {
          // Fallback to default position
          position = { x: 0, y: 0 };
          console.warn('Using fallback position for node:', {
            nodeId: node.id,
            node,
            reason: 'No valid position found'
          });
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

      console.log('Final processed nodes:', processedNodes.map(n => ({
        id: n.id,
        position: n.position,
        label: n.data.label,
        classes: n.classes
      })));

      setNodes(processedNodes);
    } catch (error) {
      console.error('Error updating nodes:', error);
    }
  }, [nodes, isDragging, draggedNodeId]);

  return {
    nodes,
    updateNodes
  };
}
