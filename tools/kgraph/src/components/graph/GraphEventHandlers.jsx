import { isValidViewport, getDefaultViewport } from '../../utils/viewport';

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

  // Handle viewport changes
  cy.on('viewport', () => {
    const newViewport = {
      zoom: cy.zoom(),
      x: cy.pan().x,
      y: cy.pan().y
    };

    if (isValidViewport(newViewport)) {
      onViewportChange(newViewport);
    }
  });

  // Return cleanup function
  return () => {
    cy.removeListener('tap');
    cy.removeListener('dragstart');
    cy.removeListener('drag');
    cy.removeListener('dragfree');
    cy.removeListener('viewport');
  };
};

export const setInitialViewport = (cy, viewport) => {
  // Temporarily disable user interactions while setting viewport
  cy.userZoomingEnabled(false);
  cy.userPanningEnabled(false);

  try {
    if (viewport && isValidViewport(viewport)) {
      // Apply saved viewport
      cy.zoom(viewport.zoom);
      cy.pan({ x: viewport.x, y: viewport.y });
      console.log('[GraphEventHandlers] Applied viewport:', viewport);
    } else {
      // Reset to default view
      const defaultViewport = getDefaultViewport();
      cy.zoom(defaultViewport.zoom);
      cy.pan({ x: defaultViewport.x, y: defaultViewport.y });
      cy.fit(undefined, 50);
      console.log('[GraphEventHandlers] Applied default viewport:', defaultViewport);
    }
  } catch (error) {
    console.error('[GraphEventHandlers] Error setting viewport:', error);
    // Fallback to safe defaults
    cy.zoom(1);
    cy.pan({ x: 0, y: 0 });
    cy.fit(undefined, 50);
  }

  // Re-enable user interactions
  cy.userZoomingEnabled(true);
  cy.userPanningEnabled(true);
};
