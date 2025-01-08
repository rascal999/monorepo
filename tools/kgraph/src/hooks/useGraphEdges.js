import { useState, useEffect } from 'react';

export function useGraphEdges(graph) {
  const [edges, setEdges] = useState([]);

  // Update edges when graph changes
  useEffect(() => {
    if (!graph) {
      setEdges([]);
      return;
    }

    // Validate graph structure
    if (!Array.isArray(graph.edges) || !Array.isArray(graph.nodes)) {
      console.error('Invalid graph structure:', graph);
      return;
    }

    try {
      // Track processed edge IDs to prevent duplicates
      const processedIds = new Set();
      const validNodeIds = new Set(graph.nodes.map(node => node.id));

      // Process edges with validation
      const processedEdges = graph.edges.reduce((acc, edge) => {
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

        // Add validated edge in Cytoscape format
        acc.push({
          data: {
            id: edgeId,
            source: edge.source,
            target: edge.target,
            ...edge.data
          }
        });
        return acc;
      }, []);

      setEdges(processedEdges);
    } catch (error) {
      console.error('Error updating edges:', error);
    }
  }, [graph]);

  return { edges };
}
