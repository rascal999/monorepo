// Validate graph structure and log any issues
export const validateGraph = (graph) => {
  if (!graph) return false;

  console.log('Validating graph structure:', {
    graphId: graph.id,
    nodeCount: graph.nodes?.length,
    edgeCount: graph.edges?.length
  });

  // Check for nodes without positions or labels
  const invalidNodes = graph.nodes?.filter(
    node => !node.position?.x || !node.position?.y || !node.data?.label
  );

  if (invalidNodes?.length > 0) {
    console.error('Found nodes with invalid structure:', invalidNodes);
    return false;
  }

  // Check for edges with invalid references
  const nodeIds = new Set(graph.nodes?.map(n => n.id) || []);
  const invalidEdges = graph.edges?.filter(
    edge => !edge.source || !edge.target || !nodeIds.has(edge.source) || !nodeIds.has(edge.target)
  );

  if (invalidEdges?.length > 0) {
    console.error('Found edges with invalid references:', invalidEdges);
    return false;
  }

  return true;
};

// Validate Cytoscape elements after initialization
export const validateCytoscapeElements = (cy) => {
  const invalidElements = cy.elements().filter(ele => {
    if (ele.isNode()) {
      return !ele.data('label') || !ele.position() || 
             typeof ele.position().x !== 'number' || 
             typeof ele.position().y !== 'number';
    }
    if (ele.isEdge()) {
      return !ele.data('source') || !ele.data('target') ||
             !cy.getElementById(ele.data('source')).length ||
             !cy.getElementById(ele.data('target')).length;
    }
    return false;
  });

  if (invalidElements.length > 0) {
    console.error('Found invalid Cytoscape elements:', 
      invalidElements.map(ele => ({
        group: ele.group(),
        data: ele.data(),
        position: ele.position()
      }))
    );
    return false;
  }

  return true;
};

// Log initial Cytoscape elements for debugging
export const logCytoscapeElements = (cy) => {
  console.log('Initial Cytoscape elements:', {
    nodes: cy.nodes().map(n => ({
      id: n.id(),
      data: n.data(),
      position: n.position()
    })),
    edges: cy.edges().map(e => ({
      id: e.id(),
      data: e.data()
    }))
  });
};
