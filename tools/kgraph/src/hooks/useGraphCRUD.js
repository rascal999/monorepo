import { useGraphCreate } from './useGraphCreate';
import { useGraphDelete } from './useGraphDelete';
import { useGraphModify } from './useGraphModify';
import { useGraphLoading } from './useGraphLoading';

export function useGraphCRUD(graphs, setGraphs, setActiveGraph) {
  const { createGraph } = useGraphCreate(setGraphs, setActiveGraph);
  const { deleteGraph } = useGraphDelete(setGraphs, setActiveGraph);
  const { updateGraph } = useGraphModify(graphs, setGraphs, setActiveGraph);
  const { setNodeLoading } = useGraphLoading(setGraphs, setActiveGraph);

  return {
    createGraph,
    updateGraph,
    deleteGraph,
    setNodeLoading
  };
}
