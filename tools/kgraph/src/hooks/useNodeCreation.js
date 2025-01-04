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

    // Check if a node with this term already exists
    const existingNode = activeGraph.nodes.find(node => 
      node.data.label.toLowerCase() === term.toLowerCase()
    );

    if (existingNode) {
      console.log('Node already exists:', existingNode);
      
      // Check if edge already exists between source and existing node
      const edgeExists = activeGraph.edges.some(edge => 
        edge.source === sourceNode.id && edge.target === existingNode.id
      );

      if (!edgeExists) {
        // Create edge to existing node
        const newEdge = createEdge(sourceNode.id, existingNode.id);
        const updatedGraph = {
          ...activeGraph,
          edges: [...activeGraph.edges, newEdge]
        };
        updateGraph(updatedGraph);
      }

      return;
    }

    // If no existing node, create new one
    const childNodes = activeGraph.edges
      .filter(edge => edge.source === sourceNode.id)
      .map(edge => activeGraph.nodes.find(n => n.id === edge.target));

    // Calculate position based on existing child nodes
    const newPosition = calculateNodePosition(sourceNode, childNodes, position);
    const newNodeId = Date.now().toString();
    
    // Create new node
    const newNode = {
      id: newNodeId,
      type: 'default',
      position: newPosition,
      data: { label: term }
    };

    // Create edge from source to new node
    const newEdge = createEdge(sourceNode.id, newNodeId);

    const updatedGraph = {
      ...activeGraph,
      nodes: [...activeGraph.nodes, newNode],
      edges: [...(activeGraph.edges || []), newEdge],
      nodeData: {
        ...activeGraph.nodeData,
        [newNodeId]: {
          chat: null,
          notes: '',
          quiz: []
        }
      }
    };

    // Don't select the new node or change the current selection
    updateGraph(updatedGraph, activeGraph.lastSelectedNodeId);
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
