import React, { useRef } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch, useAppSelector } from '../store';
import { updateGraphViewport } from '../store/slices/appSlice';
import GraphToolbar from './graph/GraphToolbar';
import CytoscapeGraph from './graph/CytoscapeGraph';
import GraphEventHandlers from './graph/GraphEventHandlers';

const defaultViewport = { zoom: 1, position: { x: 0, y: 0 } };

const GraphPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const isInitializing = useRef(false);
  const isFirstNode = useRef(false);
  
  const currentGraph = useAppSelector(state => state.app.currentGraph);
  const selectedNode = useAppSelector(state => state.app.selectedNode);
  const viewport = useAppSelector(state => state.app.currentGraph?.viewport ?? defaultViewport);

  // Helper function to update visual node selection
  const updateVisualNodeSelection = () => {
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
  };

  // Update graph data when currentGraph changes
  React.useEffect(() => {
    if (!cyRef.current || !currentGraph) return;

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
        position: node.position
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
      const containerWidth = containerRef.current?.clientWidth || 900;
      const containerHeight = containerRef.current?.clientHeight || 600;
      const centerX = containerWidth / 2;
      const centerY = containerHeight / 2;
      
      cyRef.current.zoom(0.75);
      cyRef.current.center();
    } else {
      // Restore saved viewport state
      cyRef.current.zoom(currentGraph.viewport.zoom);
      cyRef.current.pan({ 
        x: -currentGraph.viewport.position.x, 
        y: -currentGraph.viewport.position.y 
      });
    }
    
    isInitializing.current = false;
  }, [currentGraph]);

  // Update visual selection when selectedNode changes
  React.useEffect(() => {
    if (!cyRef.current) return;
    updateVisualNodeSelection();
  }, [selectedNode]);

  return (
    <div className="graph-panel">
      <GraphToolbar
        currentGraph={currentGraph}
        cyRef={cyRef}
        isInitializing={isInitializing}
        onViewportUpdate={(viewport) => dispatch(updateGraphViewport(viewport))}
      />
      <div ref={containerRef} className="cytoscape-container">
        <CytoscapeGraph
          containerRef={containerRef}
          cyRef={cyRef}
          isInitializing={isInitializing}
          viewport={viewport}
          selectedNode={selectedNode}
          onNodeSelection={updateVisualNodeSelection}
        />
        <GraphEventHandlers cyRef={cyRef} />
      </div>
    </div>
  );
};

export default GraphPanel;
