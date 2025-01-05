import { useEffect } from 'react';
import TabBar from './TabBar';
import ChatPanel from './ChatPanel';
import NotesPanel from './NotesPanel';
import QuizPanel from './QuizPanel';
import { useNodeDefinitions } from '../hooks/useNodeDefinitions';
import { useNodeInteraction } from '../hooks/useNodeInteraction';

function NodePanel({ node, nodeData, onAddNode, onUpdateData, activeGraph }) {
  const {
    initializingNodes,
    loadingNodes,
    handleGetDefinition,
    handleSendMessage
  } = useNodeDefinitions(activeGraph, onUpdateData);

  const {
    activeTab,
    wasNodeClicked,
    setActiveTab,
    handleNodeChange,
    handleNodeSelect,
    handleWordClick
  } = useNodeInteraction(onAddNode);

  // Update node interaction state when node changes
  useEffect(() => {
    handleNodeChange(node?.id);
  }, [node?.id, handleNodeChange]);

  // Handle explicit node selection
  useEffect(() => {
    if (node && nodeData) {
      // Only load definition for empty chat when explicitly selected
      if (nodeData.chat?.length === 0 && wasNodeClicked) {
        handleGetDefinition(node);
      }
    }
  }, [node, nodeData, wasNodeClicked, handleGetDefinition]);

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
      />

      <div className="flex-1 overflow-auto">
        {activeTab === 'chat' && (
          <ChatPanel
            messages={nodeData?.chat || []}
            isLoading={
              // Show loading for:
              // 1. Regular chat responses
              loadingNodes.has(node.id) || 
              // 2. Any node being initialized
              initializingNodes.has(node.id)
            }
            nodeId={node.id}
            nodeLabel={node.data.label}
            onSendMessage={(text) => handleSendMessage(node, nodeData, text)}
            onWordClick={(words) => handleWordClick(node, words)}
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
