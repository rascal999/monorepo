import { useGraphValidation } from './useGraphValidation';

export function useGraphCreate(setGraphs, setActiveGraph) {
  const { validateGraph } = useGraphValidation();

  const createGraph = (title) => {
    console.log('[GraphOperations] Creating new graph', title);
    const graphId = Date.now().toString();
    const nodeId = (Date.now() + 1).toString(); // Ensure unique ID by adding 1
    // Create initial node with title as label
    const initialNode = {
      id: nodeId,
      type: 'default',
      position: { x: 250, y: 100 },
      data: { 
        label: title,
        isLoadingDefinition: true
      }
    };

    const newGraph = {
      id: parseInt(graphId),
      title: title, // Set graph title to match initial node label
      nodes: [initialNode],
      edges: [],
      nodeData: {
        [nodeId]: {
          chat: [],
          notes: '',
          quiz: [],
          isLoadingDefinition: true
        }
      },
      lastSelectedNodeId: nodeId
    };

    if (!validateGraph(newGraph)) {
      console.error('Invalid graph structure in createGraph');
      return;
    }

    // Create graph with loading state
    const graphWithLoading = {
      ...newGraph,
      nodeData: {
        [nodeId]: {
          ...newGraph.nodeData[nodeId],
          isLoadingDefinition: true
        }
      }
    };

    // Update graphs and set active synchronously
    setGraphs(prevGraphs => {
      const newGraphs = [...prevGraphs, graphWithLoading];
      // Set active graph immediately
      setActiveGraph(graphWithLoading);
      return newGraphs;
    });

    // Return the graph ID so it can be used immediately
    return graphWithLoading.id;
  };

  return {
    createGraph
  };
}
