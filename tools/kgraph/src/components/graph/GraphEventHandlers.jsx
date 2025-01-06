import { isValidViewport } from '../../utils/viewport';

export const setupEventHandlers = (cy, {
  onNodeClick,
  onNodePositionChange,
  onViewportChange,
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

  // Viewport change handler
  cy.on('viewport', () => {
    // Only update viewport if it changed due to user interaction
    if (!cy.userZoomingEnabled() && !cy.userPanningEnabled()) {
      return;
    }

    const newViewport = {
      zoom: cy.zoom(),
      x: cy.pan().x,
      y: cy.pan().y
    };

    if (isValidViewport(newViewport) && onViewportChange) {
      onViewportChange(newViewport);
    }
  });
};

export const setInitialViewport = (cy, viewport) => {
  if (viewport && isValidViewport(viewport)) {
    cy.userZoomingEnabled(false);
    cy.userPanningEnabled(false);
    cy.zoom(viewport.zoom);
    cy.pan({ x: viewport.x, y: viewport.y });
    cy.userZoomingEnabled(true);
    cy.userPanningEnabled(true);
  } else {
    cy.fit(undefined, 50);
  }
};
