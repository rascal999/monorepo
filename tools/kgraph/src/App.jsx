import { useGraphState } from './hooks/useGraphState';
import { useNodeState } from './hooks/useNodeState';
import { MainLayout } from './layouts/MainLayout';

function App() {
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
