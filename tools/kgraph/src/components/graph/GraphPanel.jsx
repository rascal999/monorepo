import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  applyNodeChanges,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useEffect, useCallback, useState } from 'react';
import CustomNode from './CustomNode';
import { isValidViewport, getDefaultViewport } from '../../utils/viewport';

const nodeTypes = {
  default: CustomNode,
};

function GraphPanel({ graph, onNodeClick, onNodePositionChange, onViewportChange, viewport }) {
  const [nodes, setNodes] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNodeId, setDraggedNodeId] = useState(null);

  // Use validated viewport or default
  const validatedViewport = isValidViewport(viewport) ? viewport : getDefaultViewport();

  const onNodesChange = useCallback((changes) => {
    setNodes((nds) => {
      const nextNodes = applyNodeChanges(changes, nds);
      
      // Ensure valid positions during dragging
      if (isDragging && draggedNodeId) {
        return nextNodes.map(node => {
          if (node.id === draggedNodeId) {
            // Ensure position values are valid numbers
            const position = {
              x: Number.isFinite(node.position?.x) ? node.position.x : 0,
              y: Number.isFinite(node.position?.y) ? node.position.y : 0
            };
            return { ...node, position };
          }
          return nds.find(n => n.id === node.id) || node;
        });
      }
      
      // Ensure valid positions for all nodes
      return nextNodes.map(node => ({
        ...node,
        position: {
          x: Number.isFinite(node.position?.x) ? node.position.x : 0,
          y: Number.isFinite(node.position?.y) ? node.position.y : 0
        }
      }));
    });
  }, [isDragging, draggedNodeId]);

  useEffect(() => {
    if (graph) {
      console.log('Graph data received:', graph);
      
      // Add styling to nodes
      const styledNodes = graph.nodes.map(node => ({
        ...node,
        // Ensure valid position when loading nodes
        position: {
          x: Number.isFinite(node.position?.x) ? node.position.x : 0,
          y: Number.isFinite(node.position?.y) ? node.position.y : 0
        },
        style: {
          width: 100,
          height: 100,
          backgroundColor: '#FCE7F3', // pink-100
          border: '4px solid #F472B6', // pink-400
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }
      }));

      // Process edges with required properties
      const styledEdges = graph.edges.map(edge => ({
        ...edge,
        id: edge.id || `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        type: 'default',
        animated: false,
        style: { 
          stroke: '#F472B6',
          strokeWidth: 3
        },
        markerEnd: {
          type: 'arrow',
          width: 20,
          height: 20,
          color: '#F472B6',
        },
      }));

      setNodes(styledNodes);
      setEdges(styledEdges);
    } else {
      setNodes([]);
      setEdges([]);
    }
  }, [graph, setNodes, setEdges]);

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
        onNodeClick={(_, node) => {
          if (!isDragging) {
            onNodeClick(node);
          }
        }}
        onNodeDragStart={(_, node) => {
          setIsDragging(true);
          setDraggedNodeId(node.id);
        }}
        onNodeDragStop={(_, node) => {
          // Use setTimeout to ensure click handler runs after drag state is cleared
          setTimeout(() => {
            setIsDragging(false);
            setDraggedNodeId(null);
            // Ensure valid position before saving
            if (node.position && Number.isFinite(node.position.x) && Number.isFinite(node.position.y)) {
              onNodePositionChange(node);
            }
          }, 0);
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
        defaultEdgeOptions={{
          type: 'default',
          style: { 
            stroke: '#F472B6',
            strokeWidth: 3
          },
          animated: false
        }}
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor="#F472B6"
          maskColor="rgba(0, 0, 0, 0.1)"
          className="!bg-[var(--panel-bg)]"
        />
      </ReactFlow>
    </div>
  );
}

export default GraphPanel;
