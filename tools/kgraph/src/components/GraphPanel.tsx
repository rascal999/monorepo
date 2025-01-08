import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch, useAppSelector } from '../store';
import { updateGraphViewport } from '../store/slices/graphSlice';
import { selectNode } from '../store/slices/nodeSlice';
import GraphToolbar from './graph/GraphToolbar';
import type { Node } from '../store/types';

const defaultViewport = { zoom: 1, position: { x: 0, y: 0 } };

const GraphPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const isInitializing = useRef(false);
  const isFirstNode = useRef(false);
  
  const currentGraph = useAppSelector(state => state.graph.currentGraph);
  const selectedNode = useAppSelector(state => state.node.selectedNode);
  const viewport = useAppSelector(state => state.graph.currentGraph?.viewport ?? defaultViewport);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

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

    // Handle node selection
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const cyNode = node.data();
      console.log('GraphPanel: Node clicked', {
        nodeId: cyNode.id,
        hasGraph: Boolean(currentGraph),
        graphId: currentGraph?.id
      });
      
      if (!currentGraph) {
        console.warn('GraphPanel: No graph data found');
        return;
      }

      const graphNode = currentGraph.nodes.find((n: Node) => n.id === cyNode.id);
      console.log('GraphPanel: Found graph node', {
        nodeId: cyNode.id,
        foundNode: Boolean(graphNode),
        nodeLabel: graphNode?.label,
        totalNodes: currentGraph.nodes.length
      });

      if (graphNode) {
        // Ensure we select the complete node with all its data
        const completeNode = {
          ...graphNode,
          properties: {
            chatHistory: graphNode.properties?.chatHistory || []
          }
        };
        console.log('GraphPanel: Selecting node', {
          id: completeNode.id,
          label: completeNode.label,
          chatHistoryLength: completeNode.properties.chatHistory.length
        });
        dispatch(selectNode({ node: completeNode }));
      }
    });

    // Handle viewport changes
    let viewportUpdateTimeout: NodeJS.Timeout;
    cy.on('viewport', () => {
      if (isInitializing.current) return;
      
      clearTimeout(viewportUpdateTimeout);
      viewportUpdateTimeout = setTimeout(() => {
        dispatch(updateGraphViewport({
          zoom: cy.zoom(),
          position: {
            x: -cy.pan().x,
            y: -cy.pan().y
          }
        }));
      }, 100);
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, []);

  // Update graph data
  useEffect(() => {
    if (!cyRef.current || !currentGraph) return;

    // Check if we need to rebuild by comparing node/edge IDs
    const currentNodeIds = cyRef.current.nodes().map(n => n.id()).sort().join(',');
    const newNodeIds = currentGraph.nodes.map(n => n.id).sort().join(',');
    const currentEdgeIds = cyRef.current.edges().map(e => e.id()).sort().join(',');
    const newEdgeIds = currentGraph.edges.map(e => e.id).sort().join(',');

    // Only rebuild if structure has changed
    if (currentNodeIds !== newNodeIds || currentEdgeIds !== newEdgeIds) {
      isInitializing.current = true;
      
      // Clear existing elements
      cyRef.current.elements().remove();
      
      // Add nodes
      currentGraph.nodes.forEach(node => {
        cyRef.current!.add({
          group: 'nodes',
          data: { 
            id: node.id,
            label: node.label
          },
          position: { 
            x: node.position.x,
            y: node.position.y
          }
        });
      });

      // Add edges
      currentGraph.edges.forEach(edge => {
        cyRef.current!.add({
          group: 'edges',
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.label
          }
        });
      });

      // If this is a new graph (only has one node), center it
      if (currentGraph.nodes.length === 1 && !isFirstNode.current) {
        isFirstNode.current = true;
        cyRef.current.zoom(0.75);
        cyRef.current.center();
        
        // Save the centered viewport state
        dispatch(updateGraphViewport({
          zoom: cyRef.current.zoom(),
          position: {
            x: -cyRef.current.pan().x,
            y: -cyRef.current.pan().y
          }
        }));
      } else {
        // Restore saved viewport state
        cyRef.current.zoom(currentGraph.viewport.zoom);
        cyRef.current.pan({ 
          x: -currentGraph.viewport.position.x, 
          y: -currentGraph.viewport.position.y 
        });
      }
      
      isInitializing.current = false;
    } else {
      // Just update node properties if needed
      currentGraph.nodes.forEach(node => {
        const cyNode = cyRef.current!.$(`node[id="${node.id}"]`);
        if (cyNode.length) {
          cyNode.data('label', node.label);
          cyNode.position(node.position);
        }
      });
    }
  }, [currentGraph]);

  // Update visual selection when selectedNode changes
  useEffect(() => {
    if (!cyRef.current) return;
    
    // Remove selection from all nodes
    cyRef.current.$('.selected').removeClass('selected');
    
    // Add selection to the selected node if one exists
    if (selectedNode) {
      const node = cyRef.current.$(`node[id="${selectedNode.id}"]`);
      if (node.length > 0) {
        node.addClass('selected');
      }
    }
  }, [selectedNode]);

  return (
    <div className="graph-panel">
      <GraphToolbar
        currentGraph={currentGraph}
        cyRef={cyRef}
        isInitializing={isInitializing}
        onViewportUpdate={(viewport) => dispatch(updateGraphViewport(viewport))}
      />
      <div ref={containerRef} className="cytoscape-container" />
    </div>
  );
};

export default GraphPanel;
