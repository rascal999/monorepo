export function useNodeCreation(activeGraph, updateGraph) {
  const addNode = (sourceNode, term) => {
    console.log('useNodeCreation.addNode called with:', { 
      sourceNode, 
      term,
      activeGraph: {
        id: activeGraph?.id,
        nodeCount: activeGraph?.nodes?.length
      }
    });

    if (!activeGraph || !sourceNode?.id || !term?.trim()) {
      console.log('useNodeCreation.addNode validation failed:', {
        hasActiveGraph: !!activeGraph,
        hasSourceNodeId: !!sourceNode?.id,
        hasTerm: !!term?.trim()
      });
      return null;
    }

    const cleanTerm = term.trim();
    const existingNode = activeGraph.nodes.find(n => 
      n.data?.label === cleanTerm
    );

    console.log('useNodeCreation checking for existing node with term:', cleanTerm);
    
    // Return existing node ID if found
    if (existingNode) {
      console.log('Found existing node:', existingNode);
      return existingNode.id;
    }

    console.log('Creating new node for term:', cleanTerm);
    // Validate source node position
    if (!sourceNode.position?.x || !sourceNode.position?.y) {
      console.error('Invalid source node position:', sourceNode.position);
      return null;
    }

    // Create new node with unique identifier
    const newNodeId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    // Debounce node creation
    const debounceTimeout = 100; // 100ms debounce
    const lastCreation = activeGraph.nodes.find(n => 
      n.id.startsWith(sourceNode.id)
    )?.id?.split('-')[0];
    
    if (lastCreation && Date.now() - parseInt(lastCreation) < debounceTimeout) {
      console.log('Debouncing node creation');
      return null;
    }

    console.log('Creating node with ID:', newNodeId);

    // Calculate number of existing child nodes
    const childNodes = activeGraph.edges.filter(edge => 
      edge.source === sourceNode.id
    ).length;

    // Use 8 slots for even distribution around the circle
    const numSlots = 8; // Number of positions around the circle
    const slotIndex = childNodes % numSlots;
    
    // Calculate angle to distribute nodes evenly in a full circle
    // Start at -22.5 degrees (-π/8) to offset first node from horizontal
    const startAngle = -Math.PI / 8;
    const angle = startAngle + (slotIndex * Math.PI * 2) / numSlots;
    
    console.log('Angle calculation:', {
      childNodes,
      slotIndex,
      startAngleDegrees: (startAngle * 180) / Math.PI,
      angleRadians: angle,
      angleDegrees: (angle * 180) / Math.PI,
      position: {
        x: Math.cos(angle),
        y: Math.sin(angle)
      }
    });

    // Fixed radius for better spacing
    const cycleCount = Math.floor(childNodes / numSlots);
    const radius = 250 + (cycleCount * 100); // Start at 250px, increase by 100px each cycle
    const position = {
      x: sourceNode.position.x + (radius * Math.cos(angle)),
      y: sourceNode.position.y + (radius * Math.sin(angle))
    };

    console.log('Calculated new node position:', {
      sourcePosition: sourceNode.position,
      newPosition: position
    });

    const newNode = {
      id: newNodeId,
      type: 'default',
      position,
      data: { 
        label: cleanTerm,
        isLoadingDefinition: true
      }
    };

    console.log('New node structure:', {
      fullNode: newNode,
      sourceNodePosition: sourceNode.position,
      activeGraphNodes: activeGraph.nodes.map(n => ({
        id: n.id,
        position: n.position,
        data: n.data
      }))
    });
    
    // Validate new node structure
    if (!newNode.position?.x || !newNode.position?.y || !newNode.data?.label) {
      console.error('Invalid new node structure:', newNode);
      return null;
    }

    // Create edge ID using consistent format
    const edgeId = `${sourceNode.id}-${newNodeId}`;
    console.log('Creating edge with ID:', edgeId);

    // Validate edge structure
    if (!sourceNode.id || !newNodeId) {
      console.error('Invalid edge structure:', {
        sourceId: sourceNode.id,
        targetId: newNodeId
      });
      return null;
    }

    // Create complete node data first
    const nodeData = {
      chat: [],
      notes: '',
      quiz: [],
      isLoadingDefinition: true
    };

    // Create edge data
    const newEdge = {
      id: edgeId,
      source: sourceNode.id,
      target: newNodeId,
      data: {} // Ensure edge has data object
    };

    // Create complete graph update
    const updatedGraph = {
      ...activeGraph,
      nodes: [...activeGraph.nodes, newNode],
      edges: [...activeGraph.edges, newEdge],
      nodeData: {
        ...activeGraph.nodeData,
        [newNodeId]: nodeData
      },
      lastSelectedNodeId: newNodeId // Set new node as selected
    };

    console.log('Graph update details:', {
      nodeCount: updatedGraph.nodes.length,
      edgeCount: updatedGraph.edges.length,
      allNodes: updatedGraph.nodes.map(n => ({
        id: n.id,
        hasData: !!n.data,
        hasLabel: !!n.data?.label,
        label: n.data?.label,
        hasNodeData: !!updatedGraph.nodeData[n.id]
      })),
      allEdges: updatedGraph.edges.map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        hasData: !!e.data
      }))
    });

    // Update graph synchronously to ensure node exists before any operations
    updateGraph(updatedGraph);

    // Return node ID after ensuring graph is updated
    return newNodeId;
  };

  return { addNode };
}
