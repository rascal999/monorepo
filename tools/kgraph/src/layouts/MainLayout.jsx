import { useEffect } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import GraphPanel from '../components/graph/GraphPanel';
import NodePanel from '../components/NodePanel';
import SidebarPanel from '../components/SidebarPanel';

export function MainLayout({
  graphs,
  activeGraph,
  selectedNode,
  onCreateGraph,
  onSelectGraph,
  onClearData,
  onNodeClick,
  onAddNode,
  onUpdateNodeData,
  onNodePositionChange,
  viewport,
  onViewportChange
}) {
  useEffect(() => {
    // Set dark theme by default
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <div className="h-screen w-screen overflow-hidden">
      <PanelGroup direction="horizontal">
        <Panel defaultSize={20} minSize={15}>
          <SidebarPanel
            graphs={graphs}
            activeGraph={activeGraph}
            onCreateGraph={onCreateGraph}
            onSelectGraph={onSelectGraph}
            onClearData={onClearData}
          />
        </Panel>
        
        <PanelResizeHandle className="resizer" />
        
        <Panel minSize={30}>
          <GraphPanel
            graph={activeGraph}
            onNodeClick={onNodeClick}
            onNodePositionChange={onNodePositionChange}
            viewport={viewport}
            onViewportChange={onViewportChange}
          />
        </Panel>
        
        <PanelResizeHandle className="resizer" />
        
        <Panel defaultSize={30} minSize={20}>
          <NodePanel
            node={selectedNode}
            nodeData={selectedNode ? activeGraph?.nodeData[selectedNode.id] : null}
            onAddNode={onAddNode}
            onUpdateData={onUpdateNodeData}
            activeGraph={activeGraph}
          />
        </Panel>
      </PanelGroup>
    </div>
  );
}
