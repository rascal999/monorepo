import { useState, useEffect } from 'react';

export function useNodeState(activeGraph, updateGraph) {
  const [selectedNode, setSelectedNode] = useState(() => {
    if (activeGraph && activeGraph.lastSelectedNodeId) {
      return activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
    }
    return null;
  });

  // Update selected node when switching graphs
  useEffect(() => {
    if (activeGraph && activeGraph.lastSelectedNodeId) {
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      setSelectedNode(lastNode);
    } else {
      setSelectedNode(null);
    }
  }, [activeGraph]);

  const handleNodeClick = (node) => {
    // Ensure we have the complete node with position from the active graph
    const completeNode = activeGraph.nodes.find(n => n.id === node.id);
    setSelectedNode(completeNode);
    // Update the graph's lastSelectedNodeId
    updateGraph(activeGraph, completeNode.id);
  };

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
        const newEdge = {
          id: `${sourceNode.id}-${existingNode.id}`,
          source: sourceNode.id,
          sourceHandle: 'bottom',
          target: existingNode.id,
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

        const updatedGraph = {
          ...activeGraph,
          edges: [...activeGraph.edges, newEdge]
        };

        updateGraph(updatedGraph);
      }

      // Select the existing node
      setSelectedNode(existingNode);
      updateGraph(activeGraph, existingNode.id);
      return;
    }

    // If no existing node, create new one
    const childNodes = activeGraph.edges
      .filter(edge => edge.source === sourceNode.id)
      .map(edge => activeGraph.nodes.find(n => n.id === edge.target));

    // Calculate position based on existing child nodes
    let newPosition;
    if (position) {
      newPosition = position;
    } else {
      const baseX = sourceNode.position.x;
      const baseY = sourceNode.position.y;
      const radius = 300; // Increased distance from parent node
      const numChildren = childNodes.length;
      
      // Calculate angle based on number of existing children
      // Start from -90 degrees (top) and spread children in a 270-degree arc
      const angleStep = numChildren > 0 ? 270 / (numChildren + 1) : 0;
      const angle = (-135 + (numChildren + 1) * angleStep) * (Math.PI / 180);
      
      // Calculate new position using polar coordinates
      newPosition = {
        x: baseX + radius * Math.cos(angle),
        y: baseY + radius * Math.sin(angle)
      };
    }

    const newNodeId = Date.now().toString();
    const newNode = {
      id: newNodeId,
      type: 'default',
      position: newPosition,
      data: { label: term }
    };

    // Create edge with all required ReactFlow properties
    const newEdge = {
      id: `${sourceNode.id}-${newNodeId}`,
      source: sourceNode.id,
      sourceHandle: 'bottom',
      target: newNodeId,
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

  const updateNodeData = (nodeId, tabName, data) => {
    if (!activeGraph) return;

    // Only update the nodeData without touching nodes or edges
    const updatedGraph = {
      ...activeGraph,
      nodeData: {
        ...activeGraph.nodeData,
        [nodeId]: {
          ...activeGraph.nodeData[nodeId],
          [tabName]: data
        }
      }
    };

    // Preserve the lastSelectedNodeId when updating chat data
    updateGraph(updatedGraph, activeGraph.lastSelectedNodeId);
  };

  const updateNodePosition = (updatedNode) => {
    const updatedGraph = {
      ...activeGraph,
      nodes: activeGraph.nodes.map(n => 
        n.id === updatedNode.id ? updatedNode : n
      )
    };
    updateGraph(updatedGraph, updatedNode.id);
    setSelectedNode(updatedNode);
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition
  };
}
