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

    // Batch node updates using requestAnimationFrame
    requestAnimationFrame(() => {
      try {
        // Track processed node IDs to prevent duplicates
        const processedIds = new Set();

        // Process nodes with validation
        const styledNodes = graph.nodes.reduce((acc, node) => {
          // Skip duplicate nodes
          if (!node || !node.id || processedIds.has(node.id)) {
            return acc;
          }
          processedIds.add(node.id);

          // Always try to preserve existing node position
          const currentNode = nodes.find(n => n.id === node.id);
          let position;
          
          if (currentNode?.position && (isDragging ? node.id === draggedNodeId : true)) {
            // Use existing position if available and either:
            // - Node is being dragged (draggedNodeId check)
            // - Or node is not being dragged (preserve all positions)
            position = { ...currentNode.position };
          } else {
            // Fallback to graph position or default
            position = {
              x: Number.isFinite(node.position?.x) ? node.position.x : 0,
              y: Number.isFinite(node.position?.y) ? node.position.y : 0
            };
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

        setNodes(styledNodes);
      } catch (error) {
        console.error('Error updating nodes:', error);
      }
    });
  };

  return {
    nodes,
    setNodes,
    onNodesChange,
    updateNodes
  };
}
