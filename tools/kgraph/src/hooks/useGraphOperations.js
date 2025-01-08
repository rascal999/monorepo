import { useGraphCRUD } from './useGraphCRUD';
import { useGraphIO } from './useGraphIO';

export function useGraphOperations(graphs, setGraphs, setActiveGraph, handleGetDefinition) {
  const {
    createGraph,
    updateGraph,
    deleteGraph,
    setNodeLoading
  } = useGraphCRUD(graphs, setGraphs, setActiveGraph);

  const {
    exportGraph,
    importGraph
  } = useGraphIO(graphs, setGraphs, setActiveGraph);

  return {
    createGraph,
    updateGraph,
    deleteGraph,
    setNodeLoading,
    exportGraph,
    importGraph
  };
}
