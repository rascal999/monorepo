import { useCallback } from 'react';
import { useNodesState, applyNodeChanges } from 'reactflow';
import { nodeColors, nodeStyle } from '../components/graph/graphStyles';

export function useGraphNodes(graph, isDragging, draggedNodeId) {
  const [nodes, setNodes] = useNodesState([]);

  const onNodesChange = useCallback((changes) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  }, []);

  const updateNodes = (graph, existingNodes) => {
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
      // Create a map of current positions
      const currentPositions = {};
      nodes.forEach(node => {
        if (node.position) {
          currentPositions[node.id] = { ...node.position };
        }
      });

      // Track processed node IDs to prevent duplicates
      const processedIds = new Set();

      // Process nodes with validation
      const styledNodes = graph.nodes.reduce((acc, node) => {
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
            position = { ...node.position };
          } else {
            // Fallback to default position
            position = { x: 0, y: 0 };
          }

          acc.push({
            ...node,
            position,
            style: {
              ...nodeStyle,
              backgroundColor: node.id === graph.lastSelectedNodeId ? nodeColors.selected.background : nodeColors.default.background,
              border: `4px solid ${node.id === graph.lastSelectedNodeId ? nodeColors.selected.border : nodeColors.default.border}`
            }
          });
          return acc;
        }, []);

      // Immediately update nodes without animation frame delay
      setNodes(styledNodes);
    } catch (error) {
      console.error('Error updating nodes:', error);
    }
  };

  return {
    nodes,
    setNodes,
    onNodesChange,
    updateNodes
  };
}
