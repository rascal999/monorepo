// Helper to validate node structure
function isValidNode(node) {
  if (!node.id || !node.position?.x || !node.position?.y || !node.data?.label) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Invalid node structure:', node);
    }
    return false;
  }
  return true;
};

// Helper to validate edge structure
function isValidEdge(edge, nodes) {
  if (!edge.data?.id || !edge.data?.source || !edge.data?.target) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Invalid edge structure:', edge);
    }
    return false;
  }

  const sourceExists = nodes.some(n => n.id === edge.data.source);
  const targetExists = nodes.some(n => n.id === edge.data.target);

  if (!sourceExists || !targetExists) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Edge references non-existent node:', {
        edge,
        sourceExists,
        targetExists
      });
    }
    return false;
  }

  return true;
};

// Process nodes and edges into Cytoscape format
export function processElements(nodes, edges) {
  const elements = [];

  // Process nodes with validation
  nodes.forEach(node => {
    if (!isValidNode(node)) return;
    elements.push({
      data: { 
        id: node.id, 
        label: node.data.label,
        ...node.data 
      },
      position: node.position
    });
  });

  // Process edges with validation
  edges.forEach(edge => {
    if (!isValidEdge(edge, nodes)) return;
    elements.push({
      group: 'edges',
      data: edge.data
    });
  });

  return elements;
};
