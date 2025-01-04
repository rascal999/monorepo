import { useCallback } from 'react';
import { useNodesState, applyNodeChanges } from 'reactflow';
import { nodeColors, nodeStyle } from '../components/graph/graphStyles';

export function useGraphNodes(graph, isDragging, draggedNodeId) {
  const [nodes, setNodes] = useNodesState([]);

  const onNodesChange = useCallback((changes) => {
    // Batch node updates using requestAnimationFrame
    requestAnimationFrame(() => {
      setNodes((nds) => {
        try {
          // Validate changes array
          if (!Array.isArray(changes)) {
            console.error('Invalid changes array:', changes);
            return nds;
          }

          const nextNodes = applyNodeChanges(changes, nds);
          
          // Validate nextNodes array
          if (!Array.isArray(nextNodes)) {
            console.error('Invalid nodes array after changes:', nextNodes);
            return nds;
          }

          // Track processed node IDs to prevent duplicates
          const processedIds = new Set();
          
          // Process nodes with validation
          const validatedNodes = nextNodes.reduce((acc, node) => {
            // Skip duplicate nodes
            if (processedIds.has(node.id)) {
              return acc;
            }
            processedIds.add(node.id);

            // Ensure node has required properties
            if (!node || !node.id) {
              return acc;
            }

            // Handle dragging case
            if (isDragging && draggedNodeId && node.id === draggedNodeId) {
              const position = {
                x: Number.isFinite(node.position?.x) ? node.position.x : 0,
                y: Number.isFinite(node.position?.y) ? node.position.y : 0
              };
              acc.push({ ...node, position });
              return acc;
            }

            // For non-dragged nodes, either keep existing position or ensure valid position
            const existingNode = nds.find(n => n.id === node.id);
            const position = existingNode ? existingNode.position : {
              x: Number.isFinite(node.position?.x) ? node.position.x : 0,
              y: Number.isFinite(node.position?.y) ? node.position.y : 0
            };

            acc.push({ ...node, position });
            return acc;
          }, []);

          return validatedNodes;
        } catch (error) {
          console.error('Error processing node changes:', error);
          return nds;
        }
      });
    });
  }, [isDragging, draggedNodeId]);

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

        // Preserve existing node positions with validation
        const existingPositions = existingNodes.reduce((acc, node) => {
          if (node && node.id && node.position) {
            acc[node.id] = {
              x: Number.isFinite(node.position.x) ? node.position.x : 0,
              y: Number.isFinite(node.position.y) ? node.position.y : 0
            };
          }
          return acc;
        }, {});
        
        // Process nodes with validation
        const styledNodes = graph.nodes.reduce((acc, node) => {
          // Skip duplicate nodes
          if (!node || !node.id || processedIds.has(node.id)) {
            return acc;
          }
          processedIds.add(node.id);

          // Ensure valid position
          const position = existingPositions[node.id] || {
            x: Number.isFinite(node.position?.x) ? node.position.x : 0,
            y: Number.isFinite(node.position?.y) ? node.position.y : 0
          };

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
