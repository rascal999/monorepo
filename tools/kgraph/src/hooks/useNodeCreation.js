export function useNodeCreation(activeGraph, updateGraph) {
  const addNode = (sourceNode, term, position) => {
    if (!activeGraph || !sourceNode) {
      console.error('Missing activeGraph or sourceNode:', { activeGraph, sourceNode });
      return;
    }
    
    if (!sourceNode.id || !sourceNode.position) {
      console.error('Invalid sourceNode:', sourceNode);
      return;
    }

    // Clean the term by removing parentheses and preserving content inside
    const cleanTerm = term.replace(/\((.*?)\)/g, '$1').trim();

    // Check if a node with this term exists (ignoring parentheses)
    const existingNode = activeGraph.nodes.find(node => {
      const cleanLabel = node.data.label.replace(/\((.*?)\)/g, '$1').trim();
      return cleanLabel.toLowerCase() === cleanTerm.toLowerCase();
    });

    if (existingNode) {
      // Check if edge already exists between source and existing node
      const edgeExists = activeGraph.edges.some(edge => 
        (edge.source === sourceNode.id && edge.target === existingNode.id) ||
        (edge.source === existingNode.id && edge.target === sourceNode.id)
      );

      if (!edgeExists && existingNode.id !== sourceNode.id) {
        // Create edge to existing node
        const newEdge = createEdge(sourceNode.id, existingNode.id);
        const updatedGraph = {
          ...activeGraph,
          edges: [...activeGraph.edges, newEdge]
        };
        updateGraph(updatedGraph);
        console.log('Connected to existing node:', existingNode.data.label);
      } else {
        console.log('Node already connected or self-reference:', existingNode.data.label);
      }
      return;
    }

    // If no existing node, create new one
    const childNodes = activeGraph.edges
      .filter(edge => edge.source === sourceNode.id)
      .map(edge => activeGraph.nodes.find(n => n.id === edge.target));

    // Calculate position based on existing child nodes
    const newPosition = calculateNodePosition(sourceNode, childNodes, position);
    // Generate a unique ID using timestamp + random suffix to prevent collisions
    const newNodeId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Batch state updates to prevent race conditions
    try {
      // Create new node
      const newNode = {
        id: newNodeId,
        type: 'default',
        position: newPosition,
        data: { label: term }
      };

      // Create edge from source to new node
      const newEdge = createEdge(sourceNode.id, newNodeId);

      // Validate existing graph state before update
      if (!Array.isArray(activeGraph.nodes) || !Array.isArray(activeGraph.edges)) {
        console.error('Invalid graph state:', activeGraph);
        return;
      }

      // Create graph update with structure and initial nodeData
      const structureUpdate = {
        ...activeGraph,
        nodes: [...activeGraph.nodes, newNode],
        edges: [...activeGraph.edges, newEdge],
        nodeData: {
          ...activeGraph.nodeData,
          [newNodeId]: {
            chat: null, // Explicitly set to null to trigger definition fetch
            notes: '',
            quiz: []
          }
        }
      };

      // Validate the structure update
      if (structureUpdate.nodes.length !== activeGraph.nodes.length + 1 ||
          structureUpdate.edges.length !== activeGraph.edges.length + 1) {
        console.error('Graph structure update validation failed');
        return;
      }

      // Let useGraphState handle nodeData synchronization
      updateGraph(structureUpdate, activeGraph.lastSelectedNodeId);
    } catch (error) {
      console.error('Error creating node:', error);
      // Attempt to recover graph state
      if (activeGraph) {
        updateGraph(activeGraph, activeGraph.lastSelectedNodeId);
      }
    }
  };

  return { addNode };
}

// Helper function to create an edge with consistent styling
function createEdge(sourceId, targetId) {
  return {
    id: `${sourceId}-${targetId}`,
    source: sourceId,
    sourceHandle: 'bottom',
    target: targetId,
    targetHandle: 'top',
    type: 'default',
    animated: false,
    style: { 
      stroke: '#F472B6',
      strokeWidth: 3
    },
    markerEnd: {
      type: 'arrow',
      width: 20,
      height: 20,
      color: '#F472B6',
    }
  };
}

// Helper function to calculate new node position
function calculateNodePosition(sourceNode, childNodes, providedPosition) {
  if (providedPosition) {
    return providedPosition;
  }

  const baseX = sourceNode.position.x;
  const baseY = sourceNode.position.y;
  const radius = 400; // Distance from parent node
  const numChildren = childNodes.length;
  
  // Calculate angle based on number of existing children
  // Start from -180 degrees and spread children in a 360-degree arc
  const angleStep = numChildren > 0 ? 360 / (numChildren + 1) : 0;
  const angle = (-180 + (numChildren + 1) * angleStep) * (Math.PI / 180);
  
  // Calculate new position using polar coordinates
  return {
    x: baseX + radius * Math.cos(angle),
    y: baseY + radius * Math.sin(angle)
  };
}
