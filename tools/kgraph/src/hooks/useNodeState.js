import { useState, useEffect } from 'react';
import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition as importedUseNodePosition } from './useNodePosition';
import { useNodeInteraction } from './useNodeInteraction';
import { useNodeDefinitions } from './useNodeDefinitions';

// Create validated version of useNodePosition
const useNodePosition = (activeGraph, updateGraph) => {
  console.log('useNodePosition called with:', {
    hasActiveGraph: !!activeGraph,
    hasUpdateGraph: !!updateGraph
  });

  const result = importedUseNodePosition(activeGraph, updateGraph);
  
  console.log('useNodePosition result:', {
    hasResult: !!result,
    hasUpdateNodePosition: result?.updateNodePosition !== undefined,
    updateNodePositionType: typeof result?.updateNodePosition
  });

  if (!result || typeof result.updateNodePosition !== 'function') {
    console.error('useNodePosition hook returned invalid result');
    // Return a default implementation to prevent undefined errors
    return {
      updateNodePosition: (update) => {
        console.error('Called fallback updateNodePosition:', update);
      }
    };
  }

  return result;
};

export function useNodeState(activeGraph, updateGraph, setNodeLoading) {
  console.log('[NodeState] Initializing with:', {
    activeGraphId: activeGraph?.id,
    lastSelectedNodeId: activeGraph?.lastSelectedNodeId,
    hasNodes: activeGraph?.nodes?.length,
    stack: new Error().stack
  });

  const { selectedNode, setSelectedNode, handleNodeClick: handleNodeClickBase } = useNodeSelection(activeGraph, updateGraph);

  // Add effect to monitor selectedNode changes
  useEffect(() => {
    console.log('[NodeState] Selected node changed:', {
      hasSelectedNode: !!selectedNode,
      nodeId: selectedNode?.id,
      nodeLabel: selectedNode?.data?.label,
      activeGraphId: activeGraph?.id,
      lastSelectedNodeId: activeGraph?.lastSelectedNodeId
    });
  }, [selectedNode, activeGraph]);
  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph, setNodeLoading);
  // Create wrapper for updateNodeData that includes lastUserSelectedNodeId
  const updateNodeDataWithSelection = (nodeId, tabName, data, isDefinitionUpdate = false) => {
    // Only pass lastUserSelectedNodeId if it's not null/undefined and different from nodeId
    const selectionId = lastUserSelectedNodeId && lastUserSelectedNodeId !== nodeId ? lastUserSelectedNodeId : null;
    updateNodeData(nodeId, tabName, data, isDefinitionUpdate, selectionId);
  };

  // Pass updateNodeDataWithSelection and activeGraph to useNodeDefinitions
  const { handleGetDefinition, handleSendMessage } = useNodeDefinitions(
    activeGraph,
    updateNodeDataWithSelection,
    (graphId, nodeId, isLoading) => {
      console.log('Setting node loading state:', { graphId, nodeId, isLoading });
      setNodeLoading(graphId, nodeId, isLoading);
    }
  );
  // Initialize node position handling
  const nodePosition = useNodePosition(activeGraph, updateGraph);
  const updateNodePosition = nodePosition?.updateNodePosition;

  // Validate updateNodePosition is a function
  useEffect(() => {
    if (typeof updateNodePosition !== 'function') {
      console.error('updateNodePosition is not a function:', {
        type: typeof updateNodePosition,
        value: updateNodePosition,
        hasActiveGraph: !!activeGraph,
        hasUpdateGraph: !!updateGraph
      });
    }
  }, [updateNodePosition, activeGraph, updateGraph]);

  // Track current graph ID to handle transitions
  const [prevGraphId, setPrevGraphId] = useState(activeGraph?.id);

  // Track the last user-selected node ID, initialized from activeGraph
  const [lastUserSelectedNodeId, setLastUserSelectedNodeId] = useState(() => 
    activeGraph?.lastSelectedNodeId || null
  );

  // Handle graph transitions and node selection
  useEffect(() => {
    const currentGraphId = activeGraph?.id;
    console.log('[NodeState] Graph transition:', {
      prevGraphId,
      currentGraphId,
      lastSelectedNodeId: activeGraph?.lastSelectedNodeId,
      hasNodes: activeGraph?.nodes?.length
    });

    // Skip if this is the initial mount
    if (prevGraphId === undefined && currentGraphId === undefined) {
      setPrevGraphId(currentGraphId);
      return;
    }

    // Handle graph transitions
    if (currentGraphId !== prevGraphId) {
      // Reset selection states
      setLastUserSelectedNodeId(null);
      setSelectedNode(null);
      setPrevGraphId(currentGraphId);

      // If new graph has nodes, select appropriate node
      if (activeGraph?.nodes?.length > 0) {
        // Try to find node with chat data first
        const nodeWithChat = activeGraph.nodes.find(n => 
          activeGraph.nodeData[n.id]?.chat?.length > 0
        );

        // Use node with chat, lastSelectedNode, or first node
        const nodeToSelect = nodeWithChat || 
          (activeGraph.lastSelectedNodeId && 
            activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId)) ||
          activeGraph.nodes[0];

        if (nodeToSelect) {
          console.log('[NodeState] Selecting node on graph change:', {
            nodeId: nodeToSelect.id,
            hasChat: !!activeGraph.nodeData[nodeToSelect.id]?.chat?.length,
            isLastSelected: nodeToSelect.id === activeGraph.lastSelectedNodeId
          });
          setSelectedNode(nodeToSelect);
          if (activeGraph.nodeData[nodeToSelect.id]?.chat?.length > 0) {
            setLastUserSelectedNodeId(nodeToSelect.id);
          }
        }
      }
    }
  }, [activeGraph?.id]);

  // Manage tab state
  const [activeTab, setActiveTab] = useState('chat');

  // Create nodeInteraction instance
  const nodeInteraction = useNodeInteraction((sourceNode, term) => {
    console.log('useNodeState nodeInteraction callback called with:', {
      sourceNode: {
        id: sourceNode?.id,
        position: sourceNode?.position
      },
      term
    });

    const nodeId = addNode(sourceNode, term);
    console.log('useNodeState addNode result:', { nodeId });

    if (nodeId?.includes('-')) {
      console.log('useNodeState calling handleGetDefinition for nodeId:', nodeId);
      handleGetDefinition({ id: nodeId });
    }
    return nodeId;
  });

  return {
    selectedNode,
    setSelectedNode,
    activeTab,
    setActiveTab,
    nodeInteraction,
    handleSendMessage,
    handleNodeClick: handleNodeClickBase, // Use handler from useNodeSelection
    addNode,
    updateNodeData: updateNodeDataWithSelection,
    updateNodePosition,
    handleGetDefinition
  };
}
