export function useGraphDelete(setGraphs, setActiveGraph) {
  const deleteGraph = (graphId) => {
    console.log('[GraphOperations] Deleting graph', graphId);

    // Clean up viewport data for the deleted graph
    localStorage.removeItem(`kgraph-viewport-${graphId}`);

    setGraphs(prevGraphs => {
      const graphIndex = prevGraphs.findIndex(g => g.id === graphId);
      const newGraphs = prevGraphs.filter(g => g.id !== graphId);
      
      // Select the previous graph (or last graph if deleting first one)
      if (newGraphs.length > 0) {
        const newIndex = Math.min(graphIndex, newGraphs.length - 1);
        const nextGraph = newGraphs[newIndex];
        console.log('[GraphOperations] Switching to graph', nextGraph.id);
        // Load saved viewport for next graph
        setActiveGraph(nextGraph);
      } else {
        console.log('[GraphOperations] No graphs left, clearing active graph');
        setActiveGraph(null);
      }
      
      return newGraphs;
    });
  };

  return {
    deleteGraph
  };
}
