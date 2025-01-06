import { useEffect } from 'react';
import { useGraphState } from './hooks/useGraphState';
import { useNodeState } from './hooks/useNodeState';
import { MainLayout } from './layouts/MainLayout';

function App() {
  // Create default Git graph if no graphs exist
  const {
    graphs,
    activeGraph,
    setActiveGraph,
    createGraph,
    updateGraph,
    deleteGraph,
    clearData,
    viewport,
    updateViewport,
    setNodeLoading
  } = useGraphState();

  const {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition,
    activeTab,
    setActiveTab,
    nodeInteraction,
    handleGetDefinition,
    handleSendMessage
  } = useNodeState(activeGraph, updateGraph, setNodeLoading);

  // Pass handleGetDefinition to useGraphState
  useEffect(() => {
    if (handleGetDefinition) {
      useGraphState.setHandleGetDefinition(handleGetDefinition);
    }
  }, [handleGetDefinition]);

  useEffect(() => {
    if (graphs.length === 0) {
      createGraph('Git');
    }
  }, [graphs.length, createGraph]);

  return (
    <MainLayout
      graphs={graphs}
      activeGraph={activeGraph}
      selectedNode={selectedNode}
      onCreateGraph={createGraph}
      onSelectGraph={setActiveGraph}
      onDeleteGraph={deleteGraph}
      onClearData={() => {
        setSelectedNode(null);
        clearData();
      }}
      onNodeClick={handleNodeClick}
      onAddNode={addNode}
      onUpdateNodeData={updateNodeData}
      onNodePositionChange={updateNodePosition}
      viewport={viewport}
      onViewportChange={updateViewport}
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      nodeInteraction={nodeInteraction}
      handleGetDefinition={handleGetDefinition}
      handleSendMessage={handleSendMessage}
    />
  );
}

export default App;
