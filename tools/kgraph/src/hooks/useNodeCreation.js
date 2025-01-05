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
        // Create a map of current node positions
        const nodePositions = {};
        activeGraph.nodes.forEach(node => {
          nodePositions[node.id] = node.position;
        });

        // Update nodes while preserving positions
        const updatedNodes = activeGraph.nodes.map(node => ({
          ...node,
          position: nodePositions[node.id]
        }));

        const updatedGraph = {
          ...activeGraph,
          nodes: updatedNodes,
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
    // Get all child nodes and ensure they exist
    const childNodes = activeGraph.edges
      .filter(edge => edge.source === sourceNode.id)
      .map(edge => activeGraph.nodes.find(n => n.id === edge.target))
      .filter(node => node !== undefined); // Filter out any undefined nodes

    // Double check child count
    const directChildCount = activeGraph.edges.reduce((count, edge) => {
      return edge.source === sourceNode.id ? count + 1 : count;
    }, 0);

    console.log('Child count verification:', {
      edgeBasedCount: directChildCount,
      nodeBasedCount: childNodes.length,
      allEdges: activeGraph.edges.map(e => `${e.source} -> ${e.target}`)
    });

    // Log all edges and nodes for debugging
    console.log('Graph state:', {
      allEdges: activeGraph.edges,
      allNodes: activeGraph.nodes,
      sourceNodeId: sourceNode.id,
      filteredEdges: activeGraph.edges.filter(edge => edge.source === sourceNode.id),
      foundChildNodes: childNodes
    });
    
    console.log('Creating new node with:', {
      sourceNodeId: sourceNode.id,
      numExistingChildren: childNodes.length,
      childNodeIds: childNodes.map(n => n.id)
    });

    // Generate a unique ID using timestamp + random suffix to prevent collisions
    const newNodeId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Create edge first to include in child count
    const newEdge = createEdge(sourceNode.id, newNodeId);
    
    // Recalculate child nodes including the new edge
    const updatedChildNodes = [
      ...childNodes,
      { id: newNodeId } // Add new node to child count
    ];
    
    try {
      // Create graph update with structure and initial nodeData
      const structureUpdate = {
        ...activeGraph,
        nodes: [
          ...activeGraph.nodes,
          {
            id: newNodeId,
            type: 'default',
            // Place new node in a circle around parent
            position: position || (() => {
              // Fixed positions for first 8 nodes in a circle
              const positions = [
                { x: 0, y: -200 },     // Top
                { x: 200, y: -200 },   // Top right
                { x: 200, y: 0 },      // Right
                { x: 200, y: 200 },    // Bottom right
                { x: 0, y: 200 },      // Bottom
                { x: -200, y: 0 },     // Left
                { x: -200, y: -200 },  // Top left
                { x: -200, y: 200 }    // Bottom left
              ];

              // Get position based on number of existing children
              const offset = positions[childNodes.length] || {
                x: Math.cos((childNodes.length * Math.PI) / 4) * 250,
                y: Math.sin((childNodes.length * Math.PI) / 4) * 250
              };

              return {
                x: sourceNode.position.x + offset.x,
                y: sourceNode.position.y + offset.y
              };
            })(),
            data: { 
              label: term.trim(),
              isLoading: false
            }
          }
        ],
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

      // Update graph while preserving current selection
      const updatedGraph = {
        ...structureUpdate,
        lastSelectedNodeId: activeGraph.lastSelectedNodeId // Keep current selection
      };
      updateGraph(updatedGraph);
    } catch (error) {
      console.error('Error creating node:', error);
      // Attempt to recover graph state
      if (activeGraph) {
        updateGraph(activeGraph);
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
