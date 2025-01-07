import { useState, useEffect, useRef } from 'react';

export function useNodeSelection(activeGraph, updateGraph, graphs) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [prevGraphId, setPrevGraphId] = useState(null);
  const lastManualNodeRef = useRef(null);

  // Debug current state
  useEffect(() => {
    console.log('[NodeSelection DEBUG] State update:', {
      selectedNodeId: selectedNode?.id,
      prevGraphId,
      activeGraphId: activeGraph?.id,
      lastSelectedNodeId: activeGraph?.lastSelectedNodeId,
      lastManualNodeId: lastManualNodeRef.current?.id,
      hasNodes: activeGraph?.nodes?.length,
      nodeIds: activeGraph?.nodes?.map(n => n.id),
      stack: new Error().stack?.split('\n').slice(0, 3)
    });
  }, [selectedNode, activeGraph, prevGraphId]);

  // Handle graph changes and selection restoration
  useEffect(() => {
    console.log('[NodeSelection DEBUG] Graph change effect triggered:', {
      hasActiveGraph: !!activeGraph,
      lastSelectedNodeId: activeGraph?.lastSelectedNodeId,
      lastManualNodeId: lastManualNodeRef.current?.id,
      hasNodes: activeGraph?.nodes?.length,
      prevGraphId,
      currentGraphId: activeGraph?.id,
      selectedNodeId: selectedNode?.id,
      stack: new Error().stack?.split('\n').slice(0, 3)
    });

    // Clear selection when no active graph
    if (!activeGraph) {
      console.log('[NodeSelection DEBUG] No active graph, clearing selection');
      setSelectedNode(null);
      setPrevGraphId(null);
      lastManualNodeRef.current = null;
      return;
    }

    // Check if actually switching graphs
    const isGraphSwitch = prevGraphId !== activeGraph.id;
    console.log('[NodeSelection DEBUG] Graph transition:', {
      isGraphSwitch,
      from: prevGraphId,
      to: activeGraph.id,
      lastManualNodeId: lastManualNodeRef.current?.id
    });

    // If switching graphs and we have a previous selection
    if (isGraphSwitch && prevGraphId && selectedNode) {
      // Find the previous graph
      const prevGraph = graphs?.find(g => g.id === parseInt(prevGraphId));
      if (prevGraph) {
        console.log('[NodeSelection DEBUG] Saving selection to previous graph:', {
          graphId: prevGraphId,
          nodeId: selectedNode.id
        });
        // Update the previous graph's lastSelectedNodeId
        updateGraph({
          ...prevGraph,
          lastSelectedNodeId: selectedNode.id
        });
      }
    }
    
    setPrevGraphId(activeGraph.id);

    // Try to restore the last selected node
    if (activeGraph.lastSelectedNodeId) {
      console.log('[NodeSelection DEBUG] Attempting to restore last selected node:', {
        lastSelectedNodeId: activeGraph.lastSelectedNodeId,
        availableNodeIds: activeGraph.nodes.map(n => n.id)
      });
      
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      if (lastNode) {
        console.log('[NodeSelection DEBUG] Successfully restored last selected node:', {
          nodeId: lastNode.id,
          isGraphSwitch,
          hasChat: !!activeGraph.nodeData[lastNode.id]?.chat?.length
        });
        setSelectedNode(lastNode);
        return;
      } else {
        console.log('[NodeSelection DEBUG] Failed to find last selected node:', {
          lastSelectedNodeId: activeGraph.lastSelectedNodeId
        });
      }
    }

    // If no last selected node or it's not found, use priority selection
    console.log('[NodeSelection DEBUG] Falling back to priority selection');
    
    const nodeWithChat = activeGraph.nodes.find(n => {
      const hasChat = !!activeGraph.nodeData[n.id]?.chat?.length;
      console.log('[NodeSelection DEBUG] Checking node for chat:', {
        nodeId: n.id,
        hasChat,
        chatLength: activeGraph.nodeData[n.id]?.chat?.length
      });
      return hasChat;
    });

    const nodeToSelect = nodeWithChat || activeGraph.nodes[0];

    if (nodeToSelect) {
      console.log('[NodeSelection DEBUG] Using priority selection:', {
        nodeId: nodeToSelect.id,
        hasChat: !!activeGraph.nodeData[nodeToSelect.id]?.chat?.length,
        isFirstNode: nodeToSelect === activeGraph.nodes[0]
      });
      setSelectedNode(nodeToSelect);
      
      // Update graph selection state
      if (activeGraph.lastSelectedNodeId !== nodeToSelect.id) {
        console.log('[NodeSelection DEBUG] Updating graph lastSelectedNodeId:', {
          from: activeGraph.lastSelectedNodeId,
          to: nodeToSelect.id
        });
        updateGraph({
          ...activeGraph,
          lastSelectedNodeId: nodeToSelect.id
        });
      }
    } else {
      console.log('[NodeSelection DEBUG] No node to select, clearing selection');
      setSelectedNode(null);
    }
  }, [activeGraph?.id]); // Only run on graph changes

  const handleNodeClick = (node, isUserClick = true) => {
    console.log('[NodeSelection DEBUG] handleNodeClick:', { 
      node,
      isUserClick,
      activeGraphId: activeGraph?.id,
      currentSelectedId: selectedNode?.id,
      stack: new Error().stack?.split('\n').slice(0, 3)
    });
    
    if (!node || !isUserClick || !activeGraph) {
      console.log('[NodeSelection DEBUG] Ignoring click:', {
        hasNode: !!node,
        isUserClick,
        hasActiveGraph: !!activeGraph
      });
      return;
    }
    
    // Only allow selecting nodes that have required data
    if (!node.data?.label) {
      console.warn('[NodeSelection DEBUG] Ignoring invalid node:', { node });
      return;
    }

    console.log('[NodeSelection DEBUG] Processing manual node selection:', {
      nodeId: node.id,
      nodeLabel: node.data?.label,
      previousSelectedId: selectedNode?.id
    });
    
    // Store manual selection
    lastManualNodeRef.current = node;
    
    // Update selection
    setSelectedNode(node);
    
    // Update graph selection state
    if (activeGraph.lastSelectedNodeId !== node.id) {
      console.log('[NodeSelection DEBUG] Updating graph lastSelectedNodeId:', {
        from: activeGraph.lastSelectedNodeId,
        to: node.id
      });
      updateGraph({
        ...activeGraph,
        lastSelectedNodeId: node.id
      });
    }
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
