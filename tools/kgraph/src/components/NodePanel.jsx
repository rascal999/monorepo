import { useEffect } from 'react';
import TabBar from './TabBar';
import ChatPanel from './ChatPanel';
import NotesPanel from './NotesPanel';
import QuizPanel from './QuizPanel';
import { useNodeDefinitions } from '../hooks/useNodeDefinitions';
import { useNodeInteraction } from '../hooks/useNodeInteraction';

function NodePanel({ node, nodeData, onAddNode, onUpdateData, activeGraph, activeTab, setActiveTab, nodeInteraction }) {
  const {
    initializingNodes,
    loadingNodes,
    handleGetDefinition,
    handleSendMessage
  } = useNodeDefinitions(activeGraph, onUpdateData);

  const {
    wasNodeClicked,
    handleNodeChange,
    handleWordClick
  } = nodeInteraction || {};

  // Provide default handlers if nodeInteraction is not provided
  const safeHandleNodeChange = handleNodeChange || (() => {});
  const safeHandleWordClick = handleWordClick || (() => {});

  // Update node interaction state when node changes
  useEffect(() => {
    console.log('NodePanel node changed:', { nodeId: node?.id });
    safeHandleNodeChange(node?.id);
  }, [node?.id, safeHandleNodeChange]);

  // Handle explicit node selection
  useEffect(() => {
    console.log('NodePanel selection effect:', { node, nodeData, wasNodeClicked });
    if (node && nodeData) {
      // Only load definition for empty chat when explicitly selected
      if (nodeData.chat?.length === 0 && wasNodeClicked) {
        console.log('NodePanel getting definition');
        handleGetDefinition(node);
      }
    }
  }, [node, nodeData, wasNodeClicked, handleGetDefinition]);

  console.log('NodePanel render:', { activeTab, node });

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
            onWordClick={(words) => safeHandleWordClick(node, words)}
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
