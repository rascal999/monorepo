import ReactFlow from 'reactflow';
import 'reactflow/dist/style.css';
import { useState, useEffect } from 'react';
import CustomNode from './CustomNode';
import GraphControls from './GraphControls';
import { useGraphNodes } from '../../hooks/useGraphNodes';
import { useGraphEdges } from '../../hooks/useGraphEdges';
import { isValidViewport, getDefaultViewport } from '../../utils/viewport';
import { defaultEdgeOptions } from './graphStyles';

const nodeTypes = {
  default: CustomNode,
};

function GraphPanel({ graph, onNodeClick, onNodePositionChange, onViewportChange, viewport }) {
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNodeId, setDraggedNodeId] = useState(null);

  // Use validated viewport or default
  const validatedViewport = isValidViewport(viewport) ? viewport : getDefaultViewport();

  // Initialize graph state
  const { nodes, onNodesChange, updateNodes } = useGraphNodes(graph, isDragging, draggedNodeId);
  const { edges, onEdgesChange, updateEdges } = useGraphEdges();

  // Update nodes and edges when graph changes
  useEffect(() => {
    if (graph) {
      updateNodes(graph, nodes);
      updateEdges(graph);
    } else {
      updateNodes(null, []);
      updateEdges(null);
    }
  }, [graph]);

  if (!graph) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Create or select a graph to get started
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(event, node) => {
          // Only handle click if not dragging
          if (!isDragging && event.detail > 0) {
            onNodeClick(node);
          }
        }}
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
