import { useEffect } from 'react';
import TabBar from './TabBar';
import ChatPanel from './ChatPanel';
import NotesPanel from './NotesPanel';
import QuizPanel from './QuizPanel';
import SourcesPanel from './SourcesPanel';
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
  handleSendMessage
}) {
  const { handleWordClick } = nodeInteraction || {};

  // Switch to chat tab when chat updates occur
  useEffect(() => {
    if (nodeData?.chat?.length > 0 && activeTab !== 'chat') {
      setActiveTab('chat');
    }
  }, [nodeData?.chat?.length, activeTab, setActiveTab]);

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
            messages={nodeData?.chat}
            isLoading={nodeData?.isLoadingDefinition}
            nodeId={node.id}
            nodeLabel={node.data.label}
            nodeData={nodeData}
            onSendMessage={(text, onStream) => handleSendMessage(node, nodeData, text, onStream)}
            onWordClick={(words) => {
              if (!handleWordClick) return;
              handleWordClick(node, words);
            }}
            updateNodeData={onUpdateData}
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

        {activeTab === 'sources' && (
          <SourcesPanel 
            selectedNode={node}
            nodeData={nodeData}
            onUpdateData={onUpdateData}
          />
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
