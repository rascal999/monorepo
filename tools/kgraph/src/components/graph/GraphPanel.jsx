import CytoscapeComponent from 'react-cytoscapejs';
import { useState, useEffect, useRef } from 'react';
import { useForceLayout } from '../../hooks/useForceLayout';
import { useGraphNodes } from '../../hooks/useGraphNodes';
import { useGraphEdges } from '../../hooks/useGraphEdges';
import { isValidViewport, getDefaultViewport } from '../../utils/viewport';
import { cytoscapeStylesheet } from './graphStyles';

// Merge base styles with dark mode styles
const getDarkModeStyles = (baseStyles) => [
  ...baseStyles,
  {
    selector: 'node',
    style: {
      'background-color': '#6366f1',
      'border-color': '#4338ca',
      'border-width': 2,
      'label': 'data(label)',
      'color': '#fff',
      'text-valign': 'center',
      'text-halign': 'center',
      'width': 180,
      'height': 50,
      'font-size': 14,
      'font-weight': 500,
      'padding': '12px',
      'transition-property': 'background-color, border-color, width, height',
      'transition-duration': '0.3s',
      'text-outline-color': '#4338ca',
      'text-outline-width': 1,
      'border-opacity': 0.8,
      'shape': 'round-rectangle',
      // Replace shadow with border effects for depth
      'border-width': 3,
      'border-style': 'solid',
      'background-opacity': 0.95
    }
  },
  {
    selector: 'node:selected',
    style: {
      'background-color': '#818cf8',
      'border-color': '#4f46e5',
      'width': 190,
      'height': 55,
      'transition-timing-function': 'ease-out-cubic'
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 3,
      'line-color': '#94a3b8',
      'target-arrow-color': '#94a3b8',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 1.5,
      'transition-property': 'line-color, target-arrow-color, width',
      'transition-duration': '0.3s',
      'opacity': 0.8
    }
  },
  {
    selector: 'edge:selected',
    style: {
      'line-color': '#475569',
      'target-arrow-color': '#475569',
      'width': 4,
      'transition-timing-function': 'ease-out-cubic'
    }
  }
];

function GraphPanel({ graph, onNodeClick, onNodePositionChange, onViewportChange, viewport }) {
  // Refs
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const prevGraphIdRef = useRef(graph?.id);
  const prevViewportRef = useRef(viewport);

  // State
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNodeId, setDraggedNodeId] = useState(null);
  const [dimensions, setDimensions] = useState({ width: 1000, height: 800 });
  const [isDarkMode, setIsDarkMode] = useState(() => 
    document.documentElement.classList.contains('dark')
  );

  // Initialize graph state
  const { nodes, updateNodes } = useGraphNodes(graph, isDragging, draggedNodeId);
  const { edges, updateEdges } = useGraphEdges();

  // Validate graph structure
  useEffect(() => {
    if (!graph) return;

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
    }

    // Check for edges with invalid references
    const nodeIds = new Set(graph.nodes?.map(n => n.id) || []);
    const invalidEdges = graph.edges?.filter(
      edge => !edge.source || !edge.target || !nodeIds.has(edge.source) || !nodeIds.has(edge.target)
    );

    if (invalidEdges?.length > 0) {
      console.error('Found edges with invalid references:', invalidEdges);
    }
  }, [graph?.id, graph?.nodes?.length, graph?.edges?.length]);

  // Validate and convert nodes and edges to Cytoscape format
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

    if (!edge.id || !edge.source || !edge.target) {
      console.error('Invalid edge structure:', edge);
      return;
    }

    // Verify source and target nodes exist
    const sourceExists = nodes.some(n => n.id === edge.source);
    const targetExists = nodes.some(n => n.id === edge.target);

    if (!sourceExists || !targetExists) {
      console.error('Edge references non-existent node:', {
        edge,
        sourceExists,
        targetExists
      });
      return;
    }

    elements.push({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        ...edge.data
      }
    });
  });

  console.log('Final Cytoscape elements:', elements.map(el => ({
    id: el.data.id,
    type: el.position ? 'node' : 'edge',
    data: el.data,
    position: el.position
  })));

  // Effects
  // Dark mode observer
  useEffect(() => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          setIsDarkMode(document.documentElement.classList.contains('dark'));
        }
      });
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    });

    return () => observer.disconnect();
  }, []);

  // Container dimensions
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Update nodes and edges when graph or its nodes change
  useEffect(() => {
    if (graph) {
      updateNodes(graph, nodes);
      updateEdges(graph);
    } else {
      updateNodes(null, []);
      updateEdges(null);
    }
  }, [graph?.id, graph?.nodes]); // Update when graph ID or nodes change

  // Handle force layout position updates
  const handlePositionsCalculated = (positions) => {
    if (!positions || !cyRef.current) return;
    
    positions.forEach(({ id, position }) => {
      const node = cyRef.current.getElementById(id);
      if (node) {
        node.position(position);
      }
    });

    // Update graph with new positions
    if (graph) {
      const updatedNodes = nodes.map(node => {
        const element = cyRef.current.getElementById(node.id);
        return element ? { 
          ...node, 
          position: element.position() 
        } : node;
      });

      const updatedGraph = {
        ...graph,
        nodes: updatedNodes
      };
      onNodePositionChange(updatedGraph);
    }
  };

  // Apply force layout
  useForceLayout(nodes, edges, dimensions.width, dimensions.height, handlePositionsCalculated);

  const handleInit = (cy) => {
    console.log('Cytoscape initialization');
    cyRef.current = cy;

    // Validate all elements after initialization
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
    }

    // Log initial elements
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

    // Set up event handlers first
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

    cy.on('dragstart', 'node', (evt) => {
      setDraggedNodeId(evt.target.id());
    });

    cy.on('drag', 'node', () => {
      if (!isDragging) {
        setIsDragging(true);
      }
    });

    cy.on('dragfree', 'node', (evt) => {
      if (isDragging) {
        const node = evt.target;
        onNodePositionChange({
          id: node.id(),
          position: node.position()
        });
      }
      setIsDragging(false);
      setDraggedNodeId(null);
    });

    cy.on('viewport', () => {
      // Only update viewport if it changed due to user interaction
      if (!cyRef.current.userZoomingEnabled() && !cyRef.current.userPanningEnabled()) {
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

    // Then set initial viewport
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

  if (!graph) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Create or select a graph to get started
      </div>
    );
  }

  return (
    <div ref={containerRef} className="h-full w-full bg-[var(--background)]">
      <CytoscapeComponent
        elements={elements}
        style={{ width: '100%', height: '100%' }}
        stylesheet={isDarkMode ? getDarkModeStyles(cytoscapeStylesheet) : cytoscapeStylesheet}
        cy={handleInit}
        minZoom={0.1}
        maxZoom={4}
        autoungrabify={false}
        boxSelectionEnabled={false}
        wheelSensitivity={0.3}
      />
    </div>
  );
}

export default GraphPanel;
