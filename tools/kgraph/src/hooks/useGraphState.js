import { useGraphPersistence } from './useGraphPersistence';
import { useViewportState } from './useViewportState';
import { useGraphOperations } from './useGraphOperations';

export function useGraphState() {
  const {
    graphs,
    setGraphs,
    activeGraph,
    setActiveGraph,
    clearData: clearPersistentData
  } = useGraphPersistence();

  const {
    viewport,
    updateViewport,
    resetViewport
  } = useViewportState();

  const {
    createGraph,
    updateGraph
  } = useGraphOperations(setGraphs, setActiveGraph);

  const clearData = () => {
    clearPersistentData();
    resetViewport();
    setGraphs([]);
    setActiveGraph(null);
    return null;
  };

  return {
    graphs,
    activeGraph,
    viewport,
    setActiveGraph,
    createGraph,
    updateGraph,
    updateViewport,
    clearData
  };
}
