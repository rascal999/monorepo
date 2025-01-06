export const setupEventHandlers = (cy, {
  onNodeClick,
  onNodePositionChange,
  setIsDragging,
  setDraggedNodeId,
  isDragging,
  graph
}) => {
  // Node click handler
  cy.on('tap', 'node', (evt) => {
    if (!isDragging) {
      const nodeData = evt.target.data();
      const nodePosition = evt.target.position();
      const node = {
        id: nodeData.id,
        data: nodeData,
        position: nodePosition
      };
      onNodeClick(node, true);
    }
  });

  // Node drag handlers
  cy.on('dragstart', 'node', (evt) => {
    setDraggedNodeId(evt.target.id());
  });

  cy.on('drag', 'node', () => {
    if (!isDragging) {
      setIsDragging(true);
    }
  });

  cy.on('dragfree', 'node', (evt) => {
    if (isDragging && graph) {
      const node = evt.target;
      const nodeId = node.id();
      const newPosition = node.position();
      
      // Update the graph with new node position
      const updatedNodes = graph.nodes.map(n => 
        n.id === nodeId 
          ? { ...n, position: newPosition }
          : n
      );
      
      const updatedGraph = {
        ...graph,
        nodes: updatedNodes
      };
      
      onNodePositionChange(updatedGraph);
    }
    setIsDragging(false);
    setDraggedNodeId(null);
  });

  // Return cleanup function
  return () => {
    cy.removeListener('tap');
    cy.removeListener('dragstart');
    cy.removeListener('drag');
    cy.removeListener('dragfree');
  };
};
