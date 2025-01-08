import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch, useAppSelector } from '../store';
import { 
  createNode, 
  selectNode, 
  moveNode, 
  connectNodes,
  updateViewport,
  setError 
} from '../store/slices/appSlice';
import { ActionTypes } from '../store/types';

const GraphPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  
  const currentGraph = useAppSelector(state => state.app.currentGraph);
  const selectedNode = useAppSelector(state => state.app.selectedNode);
  const viewport = useAppSelector(state => state.app.viewport);

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

    // Initialize Cytoscape
    cyRef.current = cytoscape({
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
            'background-color': 'var(--primary-color)',
            'line-color': 'var(--primary-color)',
            'target-arrow-color': 'var(--primary-color)'
          }
        }
      ],
      layout: {
        name: 'grid'
      },
      zoom: viewport.zoom,
      pan: { ...viewport.position }
    });

    // Event handlers
    cyRef.current.on('tap', 'node', (evt) => {
      const node = evt.target;
      dispatch(selectNode(node.id()));
    });

    cyRef.current.on('dragfree', 'node', (evt) => {
      const node = evt.target;
      const position = node.position();
      dispatch(moveNode({ id: node.id(), position }));
    });

    // Track last focused node
    cyRef.current.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      if (!selectedNode || selectedNode.id !== node.id()) {
        dispatch(selectNode(node.id()));
      }
    });

    // Double click to create node
    let doubleClickTimer: NodeJS.Timeout;
    cyRef.current.on('tap', (evt) => {
      if (evt.target === cyRef.current) {
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

    return () => {
      cyRef.current?.destroy();
    };
  }, []);

  // Update graph data when currentGraph changes
  useEffect(() => {
    if (!cyRef.current || !currentGraph) return;

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

    cyRef.current.fit();
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
              cyRef.current.fit();
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
