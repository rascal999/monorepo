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
import { setupEventHandlers } from './GraphEventHandlers';

function GraphPanel({ graph, onNodeClick, onNodePositionChange, graphOperations }) {
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
        if (isValidViewport(viewport)) {
          cy.zoom(viewport.zoom);
          cy.pan({ x: viewport.x, y: viewport.y });
          console.log('[GraphPanel] Applied stored viewport:', viewport);
        } else {
          cy.fit(undefined, 50);
        }
      } else {
        cy.fit(undefined, 50);
      }
    }

    // Setup event handlers
    setupEventHandlers(cy, {
      onNodeClick,
      onNodePositionChange,
      setIsDragging,
      setDraggedNodeId,
      isDragging,
      graph
    });

    // Setup viewport change handler
    cy.on('viewport', () => {
      if (graph?.id) {
        const viewport = {
          zoom: cy.zoom(),
          x: cy.pan().x,
          y: cy.pan().y
        };
        localStorage.setItem(`kgraph-viewport-${graph.id}`, JSON.stringify(viewport));
        console.log('[GraphPanel] Saved viewport:', viewport);
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

  // File input ref for import
  const fileInputRef = useRef(null);

  const handleImport = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      await graphOperations.importGraph(file);
    } catch (error) {
      console.error('Import failed:', error);
      // TODO: Add proper error notification
      alert('Failed to import graph: ' + error.message);
    } finally {
      // Reset file input
      event.target.value = '';
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
    <div ref={containerRef} className="h-full w-full bg-[var(--background)] relative">
      {/* Export/Import Controls */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <button
          onClick={() => {
            console.log('[GraphPanel] Export clicked:', {
              graphId: graph.id,
              title: graph.title,
              nodesCount: graph.nodes.length,
              firstNodeLabel: graph.nodes[0]?.data?.label,
              allNodes: graph.nodes.map(n => ({
                id: n.id,
                label: n.data?.label
              }))
            });
            graphOperations.exportGraph(graph.id);
          }}
          className="px-3 py-1.5 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm"
        >
          Export
        </button>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-3 py-1.5 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm"
        >
          Import
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleImport}
          className="hidden"
        />
      </div>
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
