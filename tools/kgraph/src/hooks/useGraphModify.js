import { useCallback } from 'react';

export function useGraphModify(graphs, setGraphs, setActiveGraph) {
  const updateGraph = useCallback((updatedGraph) => {
    // Validate input
    if (!updatedGraph?.id || !Array.isArray(updatedGraph.nodes)) {
      console.error('[GraphModify] Invalid graph:', {
        hasId: Boolean(updatedGraph?.id),
        hasNodes: Array.isArray(updatedGraph?.nodes)
      });
      return;
    }

    console.log('[GraphModify] Updating graph:', {
      id: updatedGraph.id,
      nodeCount: updatedGraph.nodes.length,
      nodeDataCount: Object.keys(updatedGraph.nodeData || {}).length
    });

    // Find existing graph
    const existingGraph = graphs.find(g => g.id === updatedGraph.id);
    if (!existingGraph) {
      console.error('[GraphModify] Graph not found:', updatedGraph.id);
      return;
    }

    // Preserve existing node data
    const mergedGraph = {
      ...updatedGraph,
      nodeData: {
        ...existingGraph.nodeData,
        ...updatedGraph.nodeData
      }
    };

    console.log('[GraphModify] Merged graph:', {
      id: mergedGraph.id,
      nodeDataKeys: Object.keys(mergedGraph.nodeData),
      chatLengths: Object.entries(mergedGraph.nodeData).map(([id, data]) => ({
        id,
        chatLength: data.chat?.length
      }))
    });

    // Update graphs array
    setGraphs(prevGraphs => 
      prevGraphs.map(g => g.id === mergedGraph.id ? mergedGraph : g)
    );

    // Update active graph if needed
    setActiveGraph(prevGraph => {
      if (prevGraph?.id !== mergedGraph.id) return prevGraph;
      return mergedGraph;
    });
  }, [graphs, setGraphs, setActiveGraph]);

  return {
    updateGraph
  };
}
