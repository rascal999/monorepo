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
    setNodeLoading,
    exportGraph,
    importGraph
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
  } = useNodeState(activeGraph, updateGraph, setNodeLoading, graphs);

  // Pass handleGetDefinition to useGraphState
  useEffect(() => {
    if (handleGetDefinition) {
      useGraphState.setHandleGetDefinition(handleGetDefinition);
    }
  }, [handleGetDefinition]);

  // Create initial graph and fetch definition
  useEffect(() => {
    if (graphs.length === 0 && handleGetDefinition) {
      console.log('App: Creating initial Git graph');
      const result = createGraph('Git');
      if (result) {
        // Wait for graph state to settle before fetching definition
        const timeoutId = setTimeout(() => {
          console.log('App: Fetching definition for initial node:', result.node);
          handleGetDefinition(result.node);
        }, 100); // Add delay to ensure graph state is stable
        return () => clearTimeout(timeoutId);
      }
    }
  }, [graphs.length, createGraph, handleGetDefinition]);

  // Validate updateNodePosition before passing to MainLayout
  useEffect(() => {
    if (typeof updateNodePosition !== 'function') {
      console.error('App: updateNodePosition is not a function:', {
        type: typeof updateNodePosition,
        value: updateNodePosition,
        nodeStateKeys: Object.keys({ 
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
        })
      });
    }
  }, [updateNodePosition]);

  // Create graphOperations object from useGraphState functions
  const graphOperations = {
    exportGraph: (graphId) => {
      console.log('[App] Exporting graph:', {
        graphId,
        availableGraphs: graphs.map(g => ({
          id: g.id,
          title: g.title,
          firstNodeLabel: g.nodes[0]?.data?.label
        }))
      });
      exportGraph(graphId);
    },
    importGraph
  };

  return (
    <MainLayout
      graphs={graphs}
      activeGraph={activeGraph}
      selectedNode={selectedNode}
      onCreateGraph={(title) => {
        const result = createGraph(title);
        if (result) {
          // Wait for graph state to settle before fetching definition
          setTimeout(() => {
            handleGetDefinition(result.node);
          }, 100); // Add delay to ensure graph state is stable
        }
      }}
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
      graphOperations={graphOperations}
    />
  );
}

export default App;
