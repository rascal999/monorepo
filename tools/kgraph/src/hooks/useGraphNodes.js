import { useCallback } from 'react';
import { useNodesState, applyNodeChanges } from 'reactflow';
import { nodeColors, nodeStyle } from '../components/graph/graphStyles';

export function useGraphNodes(graph, isDragging, draggedNodeId) {
  const [nodes, setNodes] = useNodesState([]);

  const onNodesChange = useCallback((changes) => {
    setNodes((nds) => {
      const nextNodes = applyNodeChanges(changes, nds);
      
      // Ensure valid positions during dragging
      if (isDragging && draggedNodeId) {
        return nextNodes.map(node => {
          if (node.id === draggedNodeId) {
            // Ensure position values are valid numbers
            const position = {
              x: Number.isFinite(node.position?.x) ? node.position.x : 0,
              y: Number.isFinite(node.position?.y) ? node.position.y : 0
            };
            return { ...node, position };
          }
          return nds.find(n => n.id === node.id) || node;
        });
      }
      
      // Ensure valid positions for all nodes
      return nextNodes.map(node => ({
        ...node,
        position: {
          x: Number.isFinite(node.position?.x) ? node.position.x : 0,
          y: Number.isFinite(node.position?.y) ? node.position.y : 0
        }
      }));
    });
  }, [isDragging, draggedNodeId]);

  const updateNodes = (graph, existingNodes) => {
    if (!graph) {
      setNodes([]);
      return;
    }

    // Preserve existing node positions
    const existingPositions = existingNodes.reduce((acc, node) => {
      acc[node.id] = node.position;
      return acc;
    }, {});
    
    // Add styling to nodes while preserving positions
    const styledNodes = graph.nodes.map(node => ({
      ...node,
      // Use existing position if available, otherwise ensure valid position
      position: existingPositions[node.id] || {
        x: Number.isFinite(node.position?.x) ? node.position.x : 0,
        y: Number.isFinite(node.position?.y) ? node.position.y : 0
      },
      style: {
        ...nodeStyle,
        backgroundColor: node.id === graph.lastSelectedNodeId ? nodeColors.selected.background : nodeColors.default.background,
        border: `4px solid ${node.id === graph.lastSelectedNodeId ? nodeColors.selected.border : nodeColors.default.border}`
      }
    }));

    setNodes(styledNodes);
  };

  return {
    nodes,
    setNodes,
    onNodesChange,
    updateNodes
  };
}
