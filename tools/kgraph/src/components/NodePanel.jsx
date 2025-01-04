import { useState, useEffect } from 'react';
import { fetchChatCompletion } from '../services/openRouterApi';
import TabBar from './TabBar';
import ChatPanel from './ChatPanel';
import NotesPanel from './NotesPanel';
import QuizPanel from './QuizPanel';

function NodePanel({ node, nodeData, onAddNode, onUpdateData, activeGraph }) {
  const [activeTab, setActiveTab] = useState('chat');
  // Track nodes being loaded for chat responses
  const [loadingNodes, setLoadingNodes] = useState(new Set());
  // Track nodes being loaded for initial definitions
  const [initializingNodes, setInitializingNodes] = useState(new Set());

  // Track if node was explicitly selected via click
  const [wasNodeClicked, setWasNodeClicked] = useState(false);

  // Check for new nodes that need definitions
  useEffect(() => {
    if (activeGraph) {
      // Find any nodes with null chat that need definitions
      Object.entries(activeGraph.nodeData).forEach(([nodeId, data]) => {
        if (data.chat === null) {
          const node = activeGraph.nodes.find(n => n.id === nodeId);
          if (node) {
            handleGetDefinition(node);
          }
        }
      });
    }
  }, [activeGraph?.nodeData]);

  // Handle explicit node selection
  useEffect(() => {
    if (node && nodeData) {
      // Only load definition for empty chat when explicitly selected
      if (nodeData.chat?.length === 0 && wasNodeClicked) {
        handleGetDefinition(node);
      }
    }
  }, [node?.id, wasNodeClicked]);

  // Reset click state when node changes
  useEffect(() => {
    setWasNodeClicked(false);
  }, [node?.id]);

  // Handle explicit node selection
  const handleNodeSelect = () => {
    setWasNodeClicked(true);
    setActiveTab('chat');
  };

  const handleGetDefinition = async (targetNode) => {
    if (!targetNode) return;
    
    // Use different loading state for initial definitions vs chat responses
    const isInitialDefinition = !nodeData?.chat || nodeData.chat.length === 0;
    const setLoading = isInitialDefinition ? setInitializingNodes : setLoadingNodes;
    setLoading(prev => new Set([...prev, targetNode.id]));
    try {
      const messages = [
        { 
          role: 'system', 
          content: `Define "${targetNode.data.label}" in the context of "${activeGraph.title}". Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. Total response must be under 120 words.` 
        }
      ];
      
      const aiMessage = await fetchChatCompletion(messages);
      onUpdateData(targetNode.id, 'chat', [aiMessage]);
    } catch (error) {
      console.error('OpenRouter API error:', error);
      onUpdateData(targetNode.id, 'chat', [{
        role: 'assistant',
        content: 'Error fetching definition. Please check your API key and try again.'
      }]);
    } finally {
      // Clear the appropriate loading state
      const isInitialDefinition = !nodeData?.chat || nodeData.chat.length === 0;
      const setLoading = isInitialDefinition ? setInitializingNodes : setLoadingNodes;
      setLoading(prev => {
        const next = new Set(prev);
        next.delete(targetNode.id);
        return next;
      });
    }
  };

  const handleSendMessage = async (inputText) => {
    if (!node) return;

    const newMessage = { role: 'user', content: inputText };
    onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage]);
    setLoadingNodes(prev => new Set([...prev, node.id]));

    try {
      const messages = [
        { 
          role: 'system', 
          content: `Define "${node.data.label}" in the context of "${activeGraph.title}". Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. Total response must be under 120 words.` 
        },
        ...(nodeData?.chat || []),
        newMessage
      ];
      
      const aiMessage = await fetchChatCompletion(messages);
      onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage, aiMessage]);
    } catch (error) {
      console.error('OpenRouter API error:', error);
      onUpdateData(node.id, 'chat', [...(nodeData?.chat || []), newMessage, {
        role: 'assistant',
        content: 'Error: Unable to get response. Please try again.'
      }]);
    } finally {
      setLoadingNodes(prev => {
      const next = new Set(prev);
      next.delete(node.id);
      return next;
    });
    }
  };

  const handleWordClick = (words) => {
    if (node) {
      // Calculate new node position relative to source node
      // Position new node below and slightly to the right of source node
      const sourcePosition = node.position || { x: 0, y: 0 };
      const newPosition = {
        x: sourcePosition.x + 150, // Offset horizontally by 150px
        y: sourcePosition.y + 100  // Offset vertically by 100px
      };
      
      const sourceNode = {
        ...node,
        position: sourcePosition
      };
      
      onAddNode(sourceNode, words.join(' '), newPosition);
    }
  };

  if (!node) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Select a node to view details
      </div>
    );
  }

  return (
    <div className="panel h-full border-l flex flex-col">
      <TabBar 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
        onNodeSelect={handleNodeSelect}
      />

      <div className="flex-1 overflow-auto">
        {activeTab === 'chat' && (
          <ChatPanel
            messages={nodeData?.chat || []}
            isLoading={
              // Show loading for:
              // 1. Regular chat responses (loadingNodes)
              // 2. Initial node in a new graph (first node with null chat)
              // 3. Hide for other initializing nodes
              loadingNodes.has(node.id) || 
              (initializingNodes.has(node.id) && activeGraph.nodes.length === 1)
            }
            nodeId={node.id}
            nodeLabel={node.data.label}
            onSendMessage={handleSendMessage}
            onWordClick={handleWordClick}
          />
        )}

        {activeTab === 'notes' && (
          <div className="p-4">
            <NotesPanel
              value={nodeData?.notes}
              onChange={(value) => onUpdateData(node.id, 'notes', value)}
            />
          </div>
        )}

        {activeTab === 'quiz' && (
          <div className="p-4">
            <QuizPanel />
          </div>
        )}
      </div>
    </div>
  );
}

export default NodePanel;
