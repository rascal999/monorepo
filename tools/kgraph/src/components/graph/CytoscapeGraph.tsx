import React, { useEffect } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch } from '../../store';
import { selectNode, moveNode, updateGraphViewport, createNode } from '../../store/slices/appSlice';

interface CytoscapeGraphProps {
  containerRef: React.RefObject<HTMLDivElement>;
  cyRef: React.MutableRefObject<cytoscape.Core | null>;
  isInitializing: React.MutableRefObject<boolean>;
  viewport: { zoom: number; position: { x: number; y: number } };
  selectedNode: any;
  onNodeSelection: () => void;
}

const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({
  containerRef,
  cyRef,
  isInitializing,
  viewport,
  selectedNode,
  onNodeSelection
}) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (!containerRef.current) return;

    isInitializing.current = true;

    const cy = cytoscape({
      container: containerRef.current,
      minZoom: 0.1,
      maxZoom: 3,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': '30px',
            'height': '30px'
          } as cytoscape.Css.Node
        },
        {
          selector: 'edge',
          style: {
            'width': '2px',
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)'
          } as cytoscape.Css.Edge
        },
        {
          selector: '.selected',
          style: {
            'background-color': '#007bff',
            'line-color': '#007bff', 
            'target-arrow-color': '#007bff'
          } as cytoscape.Css.Node
        }
      ],
      layout: {
        name: 'grid'
      },
      userPanningEnabled: true,
      userZoomingEnabled: true,
      boxSelectionEnabled: false,
      autoungrabify: false,
      autounselectify: true
    });

    // Event handlers
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      dispatch(selectNode(node.id()));
    });

    // Handle viewport changes
    let viewportUpdateTimeout: NodeJS.Timeout;
    cy.on('viewport', () => {
      if (isInitializing.current) return;
      
      // Debounce viewport updates to prevent excessive state changes
      clearTimeout(viewportUpdateTimeout);
      viewportUpdateTimeout = setTimeout(() => {
        dispatch(updateGraphViewport({
          zoom: cy.zoom(),
          position: {
            x: -cy.pan().x,
            y: -cy.pan().y
          }
        }));
      }, 100); // Wait for 100ms of no viewport changes before updating state

      // Only update node selection if we're not currently dragging
      if (!cy.nodes(':grabbed').length) {
        onNodeSelection();
      }
    });

    // Double click to create node
    let doubleClickTimer: NodeJS.Timeout;
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        if (doubleClickTimer) {
          clearTimeout(doubleClickTimer);
          doubleClickTimer = undefined!;
          const containerWidth = containerRef.current?.clientWidth || 900;
          const containerHeight = containerRef.current?.clientHeight || 600;
          const position = {
            x: containerWidth / 2,
            y: containerHeight / 2
          };
          dispatch(createNode({ 
            label: 'New Node', 
            position
          }));
        } else {
          doubleClickTimer = setTimeout(() => {
            doubleClickTimer = undefined!;
          }, 250);
        }
      }
    });

    // Handle node movement
    cy.on('drag', 'node', () => {
      // Don't update selection during drag to prevent glitches
      clearTimeout(viewportUpdateTimeout);
    });

    cy.on('free', 'node', (evt) => {
      const node = evt.target;
      const position = node.position();
      dispatch(moveNode({ id: node.id(), position }));
    });

    cyRef.current = cy;

    // Set initial viewport
    cy.zoom(viewport.zoom);
    cy.pan({ x: -viewport.position.x, y: -viewport.position.y });
    
    isInitializing.current = false;

    return () => {
      cyRef.current?.destroy();
    };
  }, [dispatch, containerRef, viewport, onNodeSelection]);

  return null;
};

export default CytoscapeGraph;
