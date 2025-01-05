import { useEffect } from 'react';
import TabBar from './TabBar';
import ChatPanel from './ChatPanel';
import NotesPanel from './NotesPanel';
import QuizPanel from './QuizPanel';
import { useNodeInteraction } from '../hooks/useNodeInteraction';

function NodePanel({ 
  node, 
  nodeData, 
  onAddNode, 
  onUpdateData, 
  activeGraph, 
  activeTab, 
  setActiveTab, 
  nodeInteraction,
  handleGetDefinition,
  handleSendMessage
}) {

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

  // Removed automatic definition fetching - only user should trigger this

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
            isLoading={node.data.isLoading}
            nodeId={node.id}
            nodeLabel={node.data.label}
            onSendMessage={(text) => handleSendMessage(node, nodeData, text)}
            onWordClick={(words) => safeHandleWordClick(node, words)}
            handleGetDefinition={handleGetDefinition}
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
