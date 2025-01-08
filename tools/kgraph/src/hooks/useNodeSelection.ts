import { useEffect, RefObject, MutableRefObject } from 'react';
import cytoscape, { EventObject, NodeSingular, NodeDefinition } from 'cytoscape';
import { useAppDispatch } from '../store';
import { selectNode } from '../store/slices/nodeSlice';
import type { Node, Graph } from '../store/types';

interface CytoscapeNodeData extends NodeDefinition {
  data: {
    id: string;
    label: string;
    parent?: string;
  };
}

export const useNodeSelection = (
  cyRef: RefObject<cytoscape.Core | null>,
  currentGraphRef: MutableRefObject<Graph | null>,
  selectedNode: Node | null
) => {
  const dispatch = useAppDispatch();

  // Set up node selection handler
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    const handleNodeTap = (evt: EventObject) => {
      const node = evt.target as NodeSingular;
      const nodeData = node.data();
      const nodeId = nodeData.id?.toString();
      const graph = currentGraphRef.current;
      
      console.log('GraphPanel: Node clicked', {
        nodeId,
        hasGraph: Boolean(graph),
        graphId: graph?.id
      });
      
      if (!graph || !nodeId) {
        console.warn('GraphPanel: No graph data found', {
          hasGraph: Boolean(graph),
          graphId: graph?.id
        });
        return;
      }

      const graphNode = graph.nodes.find((n: Node) => n.id === nodeId);
      console.log('GraphPanel: Found graph node', {
        nodeId,
        foundNode: Boolean(graphNode),
        nodeLabel: graphNode?.label,
        totalNodes: graph.nodes.length
      });

      if (graphNode) {
        // Ensure we select the complete node with all its data
        const completeNode = {
          ...graphNode,
          properties: {
            ...graphNode.properties,
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
    };

    cy.on('tap', 'node', handleNodeTap);
    return () => {
      cy.off('tap', 'node', handleNodeTap);
    };
  }, [cyRef.current]);

  // Update visual selection when selectedNode changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    
    // Remove selection from all nodes
    cy.$('.selected').removeClass('selected');
    
    // Add selection to the selected node if one exists
    if (selectedNode) {
      const node = cy.$(`node[id="${selectedNode.id}"]`);
      if (node.length > 0) {
        node.addClass('selected');
      }
    }
  }, [selectedNode]);
};
