import { useEdgesState } from 'reactflow';
import { edgeStyle, edgeMarker } from '../components/graph/graphStyles';

export function useGraphEdges() {
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const updateEdges = (graph) => {
    if (!graph) {
      setEdges([]);
      return;
    }

    // Process edges with required properties
    const styledEdges = graph.edges.map(edge => ({
      ...edge,
      id: edge.id || `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'default',
      animated: false,
      style: edgeStyle,
      markerEnd: edgeMarker,
    }));

    setEdges(styledEdges);
  };

  return {
    edges,
    setEdges,
    onEdgesChange,
    updateEdges
  };
}
