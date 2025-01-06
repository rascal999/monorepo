import CytoscapeComponent from 'react-cytoscapejs';
import { useState, useEffect, useRef } from 'react';
import { useForceLayout } from '../../hooks/useForceLayout';
import { useGraphNodes } from '../../hooks/useGraphNodes';
import { useGraphEdges } from '../../hooks/useGraphEdges';
import { isValidViewport, getDefaultViewport } from '../../utils/viewport';
import { cytoscapeStylesheet } from './graphStyles';
import { getDarkModeStyles } from './GraphStyles';
import { validateGraph, validateCytoscapeElements, logCytoscapeElements } from './GraphValidation';
import { processElements } from './GraphElements';

function GraphPanel({ graph, onNodeClick, onNodePositionChange }) {
  // Refs
  const containerRef = useRef(null);
  const cyRef = useRef(null);

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

  // Process elements for Cytoscape
  const elements = processElements(nodes, edges);

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

  // Update nodes and edges when graph changes
  useEffect(() => {
    if (graph) {
      updateNodes(graph, nodes);
      updateEdges(graph);
    } else {
      updateNodes(null, []);
      updateEdges(null);
    }
  }, [graph?.id, graph?.nodes, graph?.edges]);

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
    cyRef.current = cy;

    validateCytoscapeElements(cy);
    logCytoscapeElements(cy);

    // Load stored viewport
    if (graph?.id) {
      const storedViewport = localStorage.getItem(`kgraph-viewport-${graph.id}`);
      if (storedViewport) {
        const viewport = JSON.parse(storedViewport);
        cy.zoom(viewport.zoom);
        cy.pan({ x: viewport.x, y: viewport.y });
        console.log('[GraphPanel] Applied stored viewport:', viewport);
      } else {
        cy.fit(undefined, 50);
      }
    }

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
      if (graph?.id) {
        const viewport = {
          zoom: cy.zoom(),
          x: cy.pan().x,
          y: cy.pan().y
        };
        localStorage.setItem(`kgraph-viewport-${graph.id}`, JSON.stringify(viewport));
      }
    });
  };

  // Cleanup event handlers
  useEffect(() => {
    return () => {
      if (cyRef.current) {
        cyRef.current.removeAllListeners();
      }
    };
  }, [graph?.id]);

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
        key={graph.id} // Force remount when graph changes
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
