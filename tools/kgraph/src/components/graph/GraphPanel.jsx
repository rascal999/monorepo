import ReactFlow from 'reactflow';
import 'reactflow/dist/style.css';
import { useState, useEffect, useRef } from 'react';
import { useForceLayout } from '../../hooks/useForceLayout';
import CustomNode from './CustomNode';
import GraphControls from './GraphControls';
import { useGraphNodes } from '../../hooks/useGraphNodes';
import { useGraphEdges } from '../../hooks/useGraphEdges';
import { isValidViewport, getDefaultViewport } from '../../utils/viewport';
import { defaultEdgeOptions } from './graphStyles';

const nodeTypes = {
  default: CustomNode,
};

function GraphPanel({ graph, onNodeClick, onNodePositionChange, onViewportChange, viewport, onGetDefinition }) {
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNodeId, setDraggedNodeId] = useState(null);

  // Use validated viewport or default
  const validatedViewport = isValidViewport(viewport) ? viewport : getDefaultViewport();

  // Initialize graph state
  const { nodes, onNodesChange, updateNodes } = useGraphNodes(graph, isDragging, draggedNodeId);
  const { edges, onEdgesChange, updateEdges } = useGraphEdges();

  // Get container dimensions for force layout
  const [dimensions, setDimensions] = useState({ width: 1000, height: 800 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    // Initial dimensions
    updateDimensions();

    // Update dimensions on window resize
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Log dimensions for debugging
  useEffect(() => {
    console.log('Container dimensions:', dimensions);
  }, [dimensions]);

  // Update nodes and edges when graph changes
  useEffect(() => {
    if (graph) {
      // Delay force layout until after initial render
      requestAnimationFrame(() => {
        updateNodes(graph, nodes);
        updateEdges(graph);
      });
    } else {
      updateNodes(null, []);
      updateEdges(null);
    }
  }, [graph]);

  // Handle force layout position updates
  const handlePositionsCalculated = (positions) => {
    if (!positions) return;
    
    // Update node positions in graph state
    const updatedNodes = nodes.map(node => {
      const newPos = positions.find(p => p.id === node.id);
      return newPos ? { ...node, position: newPos.position } : node;
    });

    // Update graph with new positions
    if (graph) {
      const updatedGraph = {
        ...graph,
        nodes: updatedNodes
      };
      onNodePositionChange(updatedGraph);
    }
  };

  // Handle node selection and definition fetching
  const handleNodeClick = (event, node) => {
    // Only handle click if not dragging
    if (!isDragging && event.detail > 0) {
      onNodeClick(node, true); // Explicit user click
      // Also trigger definition fetch for new nodes
      if (node && node.data && !node.data.chat) {
        onGetDefinition({
          id: node.id,
          data: { label: node.data.label }
        });
      }
    }
  };

  // Apply force layout only for position calculation
  useForceLayout(nodes, edges, dimensions.width, dimensions.height, handlePositionsCalculated);

  if (!graph) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Create or select a graph to get started
      </div>
    );
  }

  return (
    <div ref={containerRef} className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        onNodeDragStart={(_, node) => {
          setDraggedNodeId(node.id);
        }}
        onNodeDrag={(_, node) => {
          if (!isDragging) {
            setIsDragging(true);
          }
        }}
        onNodeDragStop={(_, node) => {
          if (isDragging && node.position) {
            onNodePositionChange(node);
          }
          setIsDragging(false);
          setDraggedNodeId(null);
        }}
        nodeTypes={nodeTypes}
        fitView={!isValidViewport(viewport) && nodes.length <= 1}
        defaultViewport={validatedViewport}
        viewport={validatedViewport}
        fitViewOptions={{ duration: 400 }}
        snapToGrid={false}
        snapGrid={[1, 1]}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
        preventScrolling={false}
        zoomOnScroll={true}
        panOnScroll={true}
        panOnDrag={true}
        onMove={(_, vp) => {
          if (onViewportChange && isValidViewport(vp)) {
            onViewportChange({
              x: vp.x,
              y: vp.y,
              zoom: vp.zoom
            });
          }
        }}
        className="bg-[var(--background)]"
        defaultEdgeOptions={defaultEdgeOptions}
      >
        <GraphControls />
      </ReactFlow>
    </div>
  );
}

export default GraphPanel;
