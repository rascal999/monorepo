import CytoscapeComponent from 'react-cytoscapejs';
import { useState, useEffect, useRef } from 'react';
import { useForceLayout } from '../../hooks/useForceLayout';
import { useGraphNodes } from '../../hooks/useGraphNodes';
import { useGraphEdges } from '../../hooks/useGraphEdges';
import { isValidViewport } from '../../utils/viewport';
import { cytoscapeStylesheet } from './graphStyles';
import { getDarkModeStyles } from './GraphStyles';
import { validateGraph, validateCytoscapeElements, logCytoscapeElements } from './GraphValidation';
import { processElements } from './GraphElements';
import { setupEventHandlers, setInitialViewport } from './GraphEventHandlers';

function GraphPanel({ graph, onNodeClick, onNodePositionChange, onViewportChange, viewport }) {
  // Early validation of props
  useEffect(() => {
    console.log('GraphPanel props:', {
      hasGraph: !!graph,
      graphId: graph?.id,
      hasOnNodeClick: !!onNodeClick,
      hasOnNodePositionChange: !!onNodePositionChange,
      hasOnViewportChange: !!onViewportChange,
      hasViewport: !!viewport
    });
  }, [graph?.id, onNodeClick, onNodePositionChange, onViewportChange, viewport]);

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
    validateGraph(graph);
  }, [graph?.id, graph?.nodes?.length, graph?.edges?.length]);

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

  // Update nodes and edges when graph or its nodes change
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
    console.log('Cytoscape initialization');
    cyRef.current = cy;

    validateCytoscapeElements(cy);
    logCytoscapeElements(cy);

    setupEventHandlers(cy, {
      onNodeClick,
      onNodePositionChange,
      onViewportChange,
      setIsDragging,
      setDraggedNodeId,
      isDragging,
      graph
    });

    setInitialViewport(cy, viewport);
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
