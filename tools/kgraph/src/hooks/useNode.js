import { useState, useEffect } from 'react';
import { fetchChatCompletion } from '../services/openRouterApi';

export function useNode(activeGraph, updateGraph, setNodeLoading) {
  // System prompt for getting definitions
  const DEFINITION_PROMPT = `You are a knowledgeable assistant helping to define concepts and explain their relationships. When given a term or concept:
1. Provide a clear, concise definition
2. Explain key aspects and relationships
3. Use academic/technical language when appropriate
4. Keep responses focused and relevant
5. Aim for 2-3 paragraphs maximum`;
  // Core node state
  const [selectedNode, setSelectedNode] = useState(() => 
    activeGraph?.lastSelectedNodeId 
      ? activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId)
      : null
  );
  const [activeTab, setActiveTab] = useState('chat');
  const [isCreatingNode, setIsCreatingNode] = useState(false);

  // Update selected node when switching graphs
  useEffect(() => {
    if (activeGraph) {
      const lastNode = activeGraph.nodes.find(n => n.id === activeGraph.lastSelectedNodeId);
      setSelectedNode(lastNode || null);
    } else {
      setSelectedNode(null);
    }
  }, [activeGraph?.id]);

  // Node selection
  const handleNodeClick = (node, isUserClick = true) => {
    if (!node) return;

    const completeNode = activeGraph.nodes.find(n => n.id === node.id);
    if (!completeNode) return;

    setSelectedNode(completeNode);
    
    if (isUserClick) {
      updateGraph({
        ...activeGraph,
        lastSelectedNodeId: completeNode.id
      });
    }

    // Reset creation state when selecting a node
    setIsCreatingNode(false);
  };

  // Node creation
  const addNode = (position) => {
    if (!activeGraph) return;

    const newNode = {
      id: `node-${Date.now()}`,
      position,
      data: { label: 'New Node', chat: [], notes: '' },
      type: 'custom'
    };

    const updatedNodes = [...activeGraph.nodes, newNode];
    updateGraph({
      ...activeGraph,
      nodes: updatedNodes,
      lastSelectedNodeId: newNode.id
    });

    setSelectedNode(newNode);
    setIsCreatingNode(false);
    return newNode;
  };

  // Node position
  const updateNodePosition = (nodeId, position) => {
    if (!activeGraph) return;

    const updatedNodes = activeGraph.nodes.map(node =>
      node.id === nodeId ? { ...node, position } : node
    );

    updateGraph({
      ...activeGraph,
      nodes: updatedNodes
    });
  };

  // Node data and AI interactions
  const updateNodeData = async (nodeId, tabName, data, isDefinitionUpdate = false) => {
    if (!activeGraph || !nodeId) return;

    // First update with initial data to ensure node visibility
    const initialUpdate = {
      ...activeGraph,
      nodes: activeGraph.nodes.map(node => {
        if (node.id === nodeId) {
          return {
            ...node,
            position: node.position,
            data: {
              ...node.data,
              [tabName]: data,
              isLoading: isDefinitionUpdate // Set loading state for definition updates
            }
          };
        }
        return node;
      })
    };
    updateGraph(initialUpdate);

    // Then handle AI updates if needed
    try {
      if (isDefinitionUpdate && typeof data === 'string') {
        setNodeLoading(true);
        const messages = [
          { role: 'system', content: DEFINITION_PROMPT },
          { role: 'user', content: `Define and explain: ${data}` }
        ];

        const aiResponse = await fetchChatCompletion(messages);
        const updatedData = {
          term: data,
          definition: aiResponse.content,
          timestamp: new Date().toISOString()
        };

        // Update with AI response while preserving position
        const finalUpdate = {
          ...activeGraph,
          nodes: activeGraph.nodes.map(node => {
            if (node.id === nodeId) {
              return {
                ...node,
                position: node.position,
                data: {
                  ...node.data,
                  [tabName]: updatedData,
                  isLoading: false
                }
              };
            }
            return node;
          })
        };
        updateGraph(finalUpdate);
        return updatedData;
      }
      return data;
    } catch (error) {
      console.error('Error updating node data:', error);
      throw error;
    } finally {
      setNodeLoading(false);
    }
  };

  // Handle getting definitions from AI
  const handleGetDefinition = async (node) => {
    if (!node?.id) return;
    
    try {
      // Find the actual node in the graph to get its label
      const actualNode = activeGraph.nodes.find(n => n.id === node.id);
      if (!actualNode?.data?.label) {
        console.error('Node not found or missing label:', node.id);
        return;
      }

      await updateNodeData(node.id, 'chat', [], true);
      const messages = [
        { role: 'system', content: DEFINITION_PROMPT },
        { role: 'user', content: `Define and explain: ${actualNode.data.label}` }
      ];
      
      setNodeLoading(true);
      const aiResponse = await fetchChatCompletion(messages);
      const chat = [
        { role: 'user', content: `What is ${actualNode.data.label}?` },
        aiResponse
      ];
      await updateNodeData(node.id, 'chat', chat);
    } catch (error) {
      console.error('Error getting definition:', error);
      throw error;
    } finally {
      setNodeLoading(false);
    }
  };

  // Handle sending messages to AI
  const handleSendMessage = async (text) => {
    if (!selectedNode) return;

    const currentChat = selectedNode.data.chat || [];
    const updatedChat = [...currentChat, { role: 'user', content: text }];

    // First update UI with user message
    await updateNodeData(selectedNode.id, 'chat', updatedChat);

    try {
      setNodeLoading(true);
      const aiResponse = await fetchChatCompletion(updatedChat);
      
      // Then update with AI response
      const finalChat = [...updatedChat, aiResponse];
      await updateNodeData(selectedNode.id, 'chat', finalChat);
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    } finally {
      setNodeLoading(false);
    }
  };

  // Node interaction
  const startNodeCreation = () => {
    setIsCreatingNode(true);
    setSelectedNode(null);
  };

  const cancelNodeCreation = () => {
    setIsCreatingNode(false);
  };

  return {
    // Core state
    selectedNode,
    activeTab,
    setActiveTab,
    isCreatingNode,

    // Node operations
    handleNodeClick,
    addNode,
    updateNodePosition,
    updateNodeData,
    startNodeCreation,
    cancelNodeCreation,
    handleSendMessage,
    handleGetDefinition
  };
}
