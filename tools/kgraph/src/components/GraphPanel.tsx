import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch, useAppSelector } from '../store';
import { 
  createNode, 
  selectNode, 
  moveNode, 
  connectNodes,
  updateGraphViewport,
  setError 
} from '../store/slices/appSlice';
import { ActionTypes } from '../store/types';

const defaultViewport = { zoom: 1, position: { x: 0, y: 0 } };

const GraphPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const isInitializing = useRef(false);
  
  const currentGraph = useAppSelector(state => state.app.currentGraph);
  const selectedNode = useAppSelector(state => state.app.selectedNode);
  const viewport = useAppSelector(state => state.app.currentGraph?.viewport ?? defaultViewport);

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          dispatch({ type: ActionTypes.IMPORT_GRAPH, payload: { data } });
        } catch (error) {
          dispatch(setError('Invalid graph file'));
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  const handleExport = () => {
    if (!currentGraph) return;
    dispatch({ type: ActionTypes.EXPORT_GRAPH });
  };

  useEffect(() => {
    if (!containerRef.current) return;

    isInitializing.current = true;

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': 30,
            'height': 30
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)'
          }
        },
        {
          selector: ':selected',
          style: {
            'background-color': '#007bff',
            'line-color': '#007bff', 
            'target-arrow-color': '#007bff'
          }
        }
      ],
      layout: {
        name: 'grid'
      }
    });

    // Event handlers
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      dispatch(selectNode(node.id()));
    });

    cy.on('dragfree', 'node', (evt) => {
      const node = evt.target;
      const position = node.position();
      dispatch(moveNode({ id: node.id(), position }));
    });

    // Track last focused node
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      if (!selectedNode || selectedNode.id !== node.id()) {
        dispatch(selectNode(node.id()));
      }
    });

    // Double click to create node
    let doubleClickTimer: NodeJS.Timeout;
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        if (doubleClickTimer) {
          // Double click - create node
          clearTimeout(doubleClickTimer);
          doubleClickTimer = undefined!;
          const position = evt.position;
          dispatch(createNode({ 
            label: 'New Node', 
            position 
          }));
        } else {
          // Single click - start timer
          doubleClickTimer = setTimeout(() => {
            doubleClickTimer = undefined!;
          }, 250);
        }
      }
    });

    // Track viewport changes
    cy.on('viewport', () => {
      if (!isInitializing.current) {
        dispatch(updateGraphViewport({
          zoom: cy.zoom(),
          position: {
            x: -cy.pan().x,
            y: -cy.pan().y
          }
        }));
      }
    });

    cyRef.current = cy;

    // Set initial viewport
    cy.zoom(viewport.zoom);
    cy.pan({ x: -viewport.position.x, y: -viewport.position.y });
    
    isInitializing.current = false;

    return () => {
      cyRef.current?.destroy();
    };
  }, [dispatch]);

  // Update graph data when currentGraph changes
  useEffect(() => {
    if (!cyRef.current) return;

    isInitializing.current = true;
    
    // Always clear existing elements
    cyRef.current.elements().remove();
    
    // Only add new elements if we have a currentGraph
    if (currentGraph) {
    
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

      // Restore viewport
      cyRef.current.zoom(currentGraph.viewport.zoom);
      cyRef.current.pan({ 
        x: -currentGraph.viewport.position.x, 
        y: -currentGraph.viewport.position.y 
      });
    } else {
      // Reset to default viewport when no graph is selected
      cyRef.current.zoom(defaultViewport.zoom);
      cyRef.current.pan({ 
        x: -defaultViewport.position.x, 
        y: -defaultViewport.position.y 
      });
    }
    
    isInitializing.current = false;
  }, [currentGraph]);

  // Update selected node
  useEffect(() => {
    if (!cyRef.current) return;
    
    cyRef.current.$('node:selected').unselect();
    if (selectedNode) {
      cyRef.current.$(`node[id="${selectedNode.id}"]`).select();
    }
  }, [selectedNode]);

  return (
    <div className="graph-panel">
      <div className="toolbar">
        <button 
          className="button button-secondary"
          onClick={() => {
            if (cyRef.current) {
              isInitializing.current = true;
              cyRef.current.fit();
              const newViewport = {
                zoom: cyRef.current.zoom(),
                position: {
                  x: -cyRef.current.pan().x,
                  y: -cyRef.current.pan().y
                }
              };
              dispatch(updateGraphViewport(newViewport));
              isInitializing.current = false;
            }
          }}
        >
          Reset View
        </button>
        <button
          className="button button-secondary"
          onClick={handleImport}
        >
          Import
        </button>
        <button
          className="button button-secondary"
          onClick={handleExport}
          disabled={!currentGraph}
        >
          Export
        </button>
      </div>
      <div ref={containerRef} className="cytoscape-container" />
    </div>
  );
};

export default GraphPanel;
