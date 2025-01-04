import { useEdgesState } from 'reactflow';
import { edgeStyle, edgeMarker } from '../components/graph/graphStyles';

export function useGraphEdges() {
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const updateEdges = (graph) => {
    if (!graph) {
      setEdges([]);
      return;
    }

    // Validate graph structure
    if (!Array.isArray(graph.edges) || !Array.isArray(graph.nodes)) {
      console.error('Invalid graph structure:', graph);
      return;
    }

    // Batch edge updates using requestAnimationFrame
    requestAnimationFrame(() => {
      try {
        // Track processed edge IDs to prevent duplicates
        const processedIds = new Set();
        const validNodeIds = new Set(graph.nodes.map(node => node.id));

        // Process edges with validation
        const styledEdges = graph.edges.reduce((acc, edge) => {
          // Skip invalid edges
          if (!edge || !edge.source || !edge.target) {
            console.warn('Invalid edge:', edge);
            return acc;
          }

          // Skip duplicate edges
          const edgeId = edge.id || `${edge.source}-${edge.target}`;
          if (processedIds.has(edgeId)) {
            return acc;
          }
          processedIds.add(edgeId);

          // Validate source and target nodes exist
          if (!validNodeIds.has(edge.source) || !validNodeIds.has(edge.target)) {
            console.warn('Edge references non-existent node:', edge);
            return acc;
          }

          // Add validated and styled edge
          acc.push({
            ...edge,
            id: edgeId,
            source: edge.source,
            target: edge.target,
            type: 'default',
            animated: false,
            style: edgeStyle,
            markerEnd: edgeMarker,
            sourceHandle: edge.sourceHandle || 'bottom',
            targetHandle: edge.targetHandle || 'top'
          });
          return acc;
        }, []);

        setEdges(styledEdges);
      } catch (error) {
        console.error('Error updating edges:', error);
      }
    });
  };

  return {
    edges,
    setEdges,
    onEdgesChange,
    updateEdges
  };
}
