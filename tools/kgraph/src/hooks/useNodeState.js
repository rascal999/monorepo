import { useState, useEffect } from 'react';
import { useNodeSelection } from './useNodeSelection';
import { useNodeCreation } from './useNodeCreation';
import { useNodeData } from './useNodeData';
import { useNodePosition } from './useNodePosition';
import { useNodeInteraction } from './useNodeInteraction';
import { useNodeDefinitions } from './useNodeDefinitions';

export function useNodeState(activeGraph, updateGraph, setNodeLoading) {
  const { selectedNode, setSelectedNode, handleNodeClick: handleNodeClickBase } = useNodeSelection(activeGraph, updateGraph);
  const { addNode } = useNodeCreation(activeGraph, updateGraph);
  const { updateNodeData } = useNodeData(activeGraph, updateGraph, setNodeLoading);
  // Create wrapper for updateNodeData that includes lastUserSelectedNodeId
  const updateNodeDataWithSelection = (nodeId, tabName, data, isDefinitionUpdate = false) => {
    updateNodeData(nodeId, tabName, data, isDefinitionUpdate, lastUserSelectedNodeId);
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
  const { updateNodePosition } = useNodePosition(activeGraph, updateGraph);

  // Track the last user-selected node ID, initialized from activeGraph
  const [lastUserSelectedNodeId, setLastUserSelectedNodeId] = useState(() => 
    activeGraph?.lastSelectedNodeId || null
  );

  // Update lastUserSelectedNodeId when switching graphs
  useEffect(() => {
    if (activeGraph?.lastSelectedNodeId) {
      setLastUserSelectedNodeId(activeGraph.lastSelectedNodeId);
    } else {
      setLastUserSelectedNodeId(null);
    }
  }, [activeGraph?.id]);

  // Manage tab state
  const [activeTab, setActiveTab] = useState('chat');

  // Create single instance of useNodeInteraction with definition handling
  const nodeInteraction = useNodeInteraction(
    (sourceNode, term, position) => {
      console.log('Adding node:', { term, position });
      const newNodeId = addNode(sourceNode, term, position);
      if (newNodeId) {
        console.log('Node added, triggering definition fetch:', newNodeId);
        // Find the new node in the graph
        const newNode = activeGraph.nodes.find(n => n.id === newNodeId);
        if (newNode) {
          handleGetDefinition(newNode);
        }
      }
      return newNodeId;
    },
    handleGetDefinition
  );


  const handleNodeClick = (node, isUserClick = true) => {
    console.log('useNodeState handleNodeClick:', { node, isUserClick });
    
    // Only update selection for explicit user clicks
    if (isUserClick) {
      // Update selected node
      handleNodeClickBase(node);
      console.log('useNodeState after handleNodeClickBase');
      
      // Update last user-selected node
      setLastUserSelectedNodeId(node.id);
      
      // Handle interaction state
      nodeInteraction.handleNodeSelect();
      console.log('useNodeState after handleNodeSelect');
    } else {
      // For non-user updates, just handle interaction state
      nodeInteraction.handleNodeChange(node?.id);
      console.log('useNodeState after handleNodeChange');
    }
  };

  return {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData: updateNodeDataWithSelection,
    updateNodePosition,
    activeTab,
    setActiveTab,
    nodeInteraction,
    handleGetDefinition,
    handleSendMessage
  };
}
