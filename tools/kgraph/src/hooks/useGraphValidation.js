export function useGraphValidation() {
  const validateGraph = (graph) => {
    // Validate basic graph structure
    if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
      console.error('Invalid graph structure:', graph);
      return false;
    }

    // Validate nodes
    const validNodes = graph.nodes.every(node => 
      node && 
      node.id && 
      node.position && 
      typeof node.position.x === 'number' && 
      typeof node.position.y === 'number' &&
      node.data?.label // Ensure label exists
    );

    if (!validNodes) {
      console.error('Invalid node data in graph');
      return false;
    }

    // Validate edges
    const validEdges = graph.edges.every(edge =>
      edge && edge.source && edge.target &&
      graph.nodes.some(n => n.id === edge.source) &&
      graph.nodes.some(n => n.id === edge.target)
    );

    if (!validEdges) {
      console.error('Invalid edge data in graph');
      return false;
    }

    return true;
  };

  const validateNodeData = (graph) => {
    if (!graph.nodeData || typeof graph.nodeData !== 'object') {
      console.error('Invalid nodeData structure');
      return false;
    }

    // Ensure all nodes have corresponding nodeData
    const allNodesHaveData = graph.nodes.every(node => {
      const data = graph.nodeData[node.id];
      return data && 
        (data.chat === null || Array.isArray(data.chat)) &&
        typeof data.notes === 'string' &&
        Array.isArray(data.quiz);
    });

    if (!allNodesHaveData) {
      console.error('Missing or invalid nodeData for some nodes');
      return false;
    }

    // Ensure no orphaned nodeData
    const validNodeIds = new Set(graph.nodes.map(n => n.id));
    const noOrphanedData = Object.keys(graph.nodeData).every(nodeId => 
      validNodeIds.has(nodeId)
    );

    if (!noOrphanedData) {
      console.error('Found orphaned nodeData');
      return false;
    }

    return true;
  };

  const validateGraphUpdate = (updatedGraph, currentGraph) => {
    // Basic structure validation
    if (!validateGraph(updatedGraph)) {
      return false;
    }

    // Node data validation
    if (!validateNodeData(updatedGraph)) {
      return false;
    }

    // Validate graph ID consistency
    if (currentGraph && updatedGraph.id !== currentGraph.id) {
      console.error('Graph ID mismatch');
      return false;
    }

    return true;
  };

  return {
    validateGraph,
    validateNodeData,
    validateGraphUpdate
  };
}
