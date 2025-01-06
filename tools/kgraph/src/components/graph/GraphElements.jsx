// Process nodes and edges into Cytoscape format
export const processElements = (nodes, edges) => {
  const elements = [];

  // Process nodes with validation
  nodes.forEach(node => {
    console.log('Processing node for Cytoscape:', {
      id: node.id,
      position: node.position,
      data: node.data
    });

    if (!node.id || !node.position?.x || !node.position?.y || !node.data?.label) {
      console.error('Invalid node structure:', node);
      return;
    }

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
    console.log('Processing edge for Cytoscape:', edge);

    if (!edge.data?.id || !edge.data?.source || !edge.data?.target) {
      console.error('Invalid edge structure:', edge);
      return;
    }

    // Verify source and target nodes exist
    const sourceExists = nodes.some(n => n.id === edge.data.source);
    const targetExists = nodes.some(n => n.id === edge.data.target);

    if (!sourceExists || !targetExists) {
      console.error('Edge references non-existent node:', {
        edge,
        sourceExists,
        targetExists
      });
      return;
    }

    elements.push({
      group: 'edges',
      data: edge.data
    });
  });

  console.log('Final Cytoscape elements:', elements.map(el => ({
    id: el.data.id,
    type: el.position ? 'node' : 'edge',
    data: el.data,
    position: el.position
  })));

  return elements;
};
