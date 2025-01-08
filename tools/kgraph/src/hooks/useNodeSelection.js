import { useState, useEffect, useRef, useCallback } from 'react';

export function useNodeSelection(activeGraph, updateGraph, graphs) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [prevGraphId, setPrevGraphId] = useState(null);
  const lastManualNodeRef = useRef(null);

  // Initialize selection state
  useEffect(() => {
    if (!activeGraph) return;

    // Only run on initial mount or graph switch
    if (selectedNode && selectedNode.id === activeGraph.lastSelectedNodeId) {
      return;
    }

    console.log('[NodeSelection] State change:', {
      hasActiveGraph: Boolean(activeGraph),
      graphId: activeGraph?.id,
      prevGraphId,
      selectedNodeId: selectedNode?.id,
      lastManualNodeId: lastManualNodeRef.current?.id,
      nodeCount: activeGraph?.nodes?.length
    });

    if (!activeGraph?.nodes?.length) {
      console.log('[NodeSelection] No nodes available');
      return;
    }

    // Find initial node to select
    const initialNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId) || 
                       activeGraph.nodes.find(n => activeGraph.nodeData[n.id]?.chat?.length > 0) || 
                       activeGraph.nodes[0];

    if (initialNode) {
      console.log('[NodeSelection] Setting initial node:', {
        id: initialNode.id,
        label: initialNode.data.label
      });
      setSelectedNode(initialNode);
    }
  }, [activeGraph]); // Only run on graph changes

  // Handle graph switches
  useEffect(() => {
    if (!activeGraph || prevGraphId === activeGraph.id) return;

    console.log('[NodeSelection] Graph switch detected:', {
      from: prevGraphId,
      to: activeGraph.id
    });

    // Save previous selection
    if (prevGraphId && selectedNode) {
      const prevGraph = graphs?.find(g => g.id === parseInt(prevGraphId));
      if (prevGraph) {
        updateGraph({
          ...prevGraph,
          lastSelectedNodeId: selectedNode.id
        });
      }
    }
    
    setPrevGraphId(activeGraph.id);

    // Try to restore selection
    if (activeGraph.lastSelectedNodeId) {
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      if (lastNode) {
        console.log('[NodeSelection] Restoring last selected node:', lastNode.id);
        setSelectedNode(lastNode);
        return;
      }
    }

    // Select best available node
    const nodeWithChat = activeGraph.nodes.find(n => {
      const hasChat = Boolean(activeGraph.nodeData[n.id]?.chat?.length);
      console.log('[NodeSelection] Checking node:', {
        id: n.id,
        hasChat,
        chatLength: activeGraph.nodeData[n.id]?.chat?.length
      });
      return hasChat;
    });

    const nodeToSelect = nodeWithChat || activeGraph.nodes[0];
    if (nodeToSelect) {
      console.log('[NodeSelection] Selecting node:', {
        id: nodeToSelect.id,
        isChat: Boolean(nodeWithChat),
        isFirst: nodeToSelect === activeGraph.nodes[0]
      });
      setSelectedNode(nodeToSelect);
      
      if (activeGraph.lastSelectedNodeId !== nodeToSelect.id) {
        updateGraph({
          ...activeGraph,
          lastSelectedNodeId: nodeToSelect.id
        });
      }
    }
  }, [activeGraph, graphs, prevGraphId, selectedNode, updateGraph]);

  const handleNodeClick = useCallback((node, isUserClick = true) => {
    console.log('[NodeSelection] Node clicked:', {
      nodeId: node?.id,
      isUserClick,
      hasActiveGraph: Boolean(activeGraph),
      hasLabel: Boolean(node?.data?.label)
    });

    if (!node || !isUserClick || !activeGraph) return;
    
    if (!node.data?.label) {
      console.warn('[NodeSelection] Invalid node:', node);
      return;
    }
    
    lastManualNodeRef.current = node;
    setSelectedNode(node);
    
    if (activeGraph.lastSelectedNodeId !== node.id) {
      updateGraph({
        ...activeGraph,
        lastSelectedNodeId: node.id
      });
    }
  }, [activeGraph, updateGraph]);

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick
  };
}
