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
    clearData,
    viewport,
    updateViewport
  } = useGraphState();

  const {
    selectedNode,
    setSelectedNode,
    handleNodeClick,
    addNode,
    updateNodeData,
    updateNodePosition,
    activeTab,
    setActiveTab
  } = useNodeState(activeGraph, updateGraph);

  return (
    <MainLayout
      graphs={graphs}
      activeGraph={activeGraph}
      selectedNode={selectedNode}
      onCreateGraph={createGraph}
      onSelectGraph={setActiveGraph}
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
    />
  );
}

export default App;
