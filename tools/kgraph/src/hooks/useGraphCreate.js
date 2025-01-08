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
        isLoadingDefinition: true // Start with loading state to trigger definition fetch
      }
    };

    const newGraph = {
      id: parseInt(graphId),
      title: title, // Set graph title to match initial node label
      nodes: [initialNode],
      edges: [],
      nodeData: {
        [nodeId]: {
          chat: [], // Initialize empty chat array
          notes: '',
          quiz: [],
          isLoadingDefinition: true // Start with loading state to trigger definition fetch
        }
      },
      lastSelectedNodeId: nodeId
    };

    if (!validateGraph(newGraph)) {
      console.error('Invalid graph structure in createGraph');
      return;
    }

    // Update graphs and set active synchronously
    setGraphs(prevGraphs => {
      const newGraphs = [...prevGraphs, newGraph];
      // Set active graph immediately
      setActiveGraph(newGraph);
      return newGraphs;
    });

    // Return the node info so definition can be fetched after graph creation
    return {
      graphId: newGraph.id,
      nodeId,
      node: {
        id: nodeId,
        data: { label: title }
      }
    };
  };

  return {
    createGraph
  };
}
