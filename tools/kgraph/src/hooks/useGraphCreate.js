import { useGraphValidation } from './useGraphValidation';

export function useGraphCreate(setGraphs, setActiveGraph) {
  const { validateGraph } = useGraphValidation();

  const createGraph = (title) => {
    console.log('[GraphCreate] Creating graph:', {
      title,
      timestamp: Date.now()
    });
    
    const graphId = Date.now().toString();
    const nodeId = (Date.now() + 1).toString(); // Ensure unique ID
    
    // Create initial node with title as label
    const initialNode = {
      id: nodeId,
      type: 'default',
      position: { x: 250, y: 100 },
      data: { 
        label: title,
        isLoadingDefinition: false // Let batch hook handle loading state
      }
    };

    const newGraph = {
      id: parseInt(graphId),
      title: title,
      nodes: [initialNode],
      edges: [],
      nodeData: {
        [nodeId]: {
          chat: [], // Initialize empty chat array
          notes: '',
          quiz: [],
          isLoadingDefinition: false // Let batch hook handle loading state
        }
      },
      lastSelectedNodeId: nodeId
    };

    console.log('[GraphCreate] Created graph:', {
      graphId: newGraph.id,
      nodeId,
      nodeState: initialNode.data,
      nodeData: newGraph.nodeData[nodeId]
    });

    if (!validateGraph(newGraph)) {
      console.error('[GraphCreate] Invalid graph structure');
      return;
    }

    // Update graphs and set active graph
    try {
      // Update graphs first
      setGraphs(prevGraphs => {
        console.log('[GraphCreate] Updating graphs:', {
          currentCount: prevGraphs.length,
          newGraphId: newGraph.id
        });
        return [...prevGraphs, newGraph];
      });

      // Then set active graph
      console.log('[GraphCreate] Setting active graph:', {
        id: newGraph.id,
        nodeCount: newGraph.nodes.length,
        hasNodeData: Boolean(newGraph.nodeData[nodeId])
      });
      setActiveGraph(newGraph);

      return {
        graphId: newGraph.id,
        nodeId,
        node: initialNode
      };
    } catch (error) {
      console.error('[GraphCreate] Error creating graph:', error);
      return null;
    }
  };

  return {
    createGraph
  };
}
