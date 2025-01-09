import { useEffect, RefObject, MutableRefObject } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch } from '../store';
import { selectNode } from '../store/slices/nodeSlice';
import { updateGraphViewport, updateNodePosition, updateNodeInGraph } from '../store/slices/graphSlice';
import type { Node, Graph, NodeProperties } from '../store/types';
import { defaultColors } from '../components/graph/GraphStyles';

export const useGraphData = (
  cyRef: RefObject<cytoscape.Core | null>,
  currentGraph: Graph | null,
  isInitializing: MutableRefObject<boolean>,
  isFirstNode: MutableRefObject<boolean>
) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (!cyRef.current || !currentGraph) {
      isFirstNode.current = false; // Reset flag when no graph is selected
      return;
    }

    const updateGraph = () => {
      const cy = cyRef.current;
      if (!cy) return;
      
      isInitializing.current = true;
      
      // Clear existing elements
      cy.elements().remove();
      
      // Add nodes
      currentGraph.nodes.forEach((node: Node) => {
        if (!cy) return;

        // Initialize or update node properties
        let properties = node.properties || {};
        if (!properties.color || !properties.gradient || !properties.border || !properties.text) {
          const scheme = defaultColors.blue;
          properties = {
            ...properties,
            chatHistory: properties.chatHistory || [],
            gradient: scheme.gradient,
            border: scheme.border,
            text: scheme.text,
            color: 'blue'
          };

          // Update node in Redux store
          dispatch(updateNodeInGraph({
            nodeId: node.id,
            changes: {
              properties
            }
          }));
        }

        cy.add({
          group: 'nodes',
          data: { 
            id: node.id,
            label: node.label,
            properties
          },
          position: { 
            x: node.position.x,
            y: node.position.y
          }
        });
      });

      // Add edges
      currentGraph.edges.forEach(edge => {
        if (!cy) return;
        cy.add({
          group: 'edges',
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.label || '' // Ensure label is never undefined
          }
        });
      });

      // If this is a new graph (only has one node), center it and select it
      if (currentGraph.nodes.length === 1 && !isFirstNode.current) {
        isFirstNode.current = true;
        cy.zoom(0.75);
        cy.center();
        
        // Save the centered viewport state
        dispatch(updateGraphViewport({
          zoom: cy.zoom(),
          position: {
            x: -cy.pan().x,
            y: -cy.pan().y
          }
        }));

        // Select the first node
        const firstNode = currentGraph.nodes[0];
        const completeNode = {
          ...firstNode,
          properties: {
            ...firstNode.properties,
            chatHistory: firstNode.properties?.chatHistory || []
          }
        };
        dispatch(selectNode({ node: completeNode }));
      } else {
        // Restore saved viewport state
        cy.zoom(currentGraph.viewport.zoom);
        cy.pan({ 
          x: -currentGraph.viewport.position.x, 
          y: -currentGraph.viewport.position.y 
        });
      }
      
      isInitializing.current = false;

      // Set up node movement listener - fires when drag is complete
      cy.on('dragfree', 'node', (event) => {
        if (!isInitializing.current) {
          const node = event.target;
          dispatch(updateNodePosition({
            nodeId: node.id(),
            position: node.position()
          }));
        }
      });
    };

    // Use a timeout to ensure Redux state is settled
    const timeoutId = setTimeout(updateGraph, 100);
    return () => {
      clearTimeout(timeoutId);
      // Clean up event listeners
      cyRef.current?.removeListener('dragfree');
    };
  }, [currentGraph]);
};
