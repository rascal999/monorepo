import { useCallback } from 'react';

export function useGraphModify(graphs, setGraphs, setActiveGraph) {
  const updateGraph = useCallback((updatedGraph, sourceNodeId) => {
    // Basic validation
    if (!updatedGraph?.id || !Array.isArray(updatedGraph.nodes)) {
      console.warn('[GraphOperations] Invalid graph update');
      return;
    }

    // Helper function to wait
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Find existing graph with retry
    const findGraph = async (retries = 3, delay = 50) => {
      for (let i = retries; i >= 0; i--) {
        const existingGraph = graphs.find(g => g.id === updatedGraph.id);
        if (existingGraph) {
          return existingGraph;
        }
        if (i > 0) {
          console.log('[GraphOperations] Graph not found, retrying...', {
            graphId: updatedGraph.id,
            remainingRetries: i - 1
          });
          await wait(delay);
        }
      }
      console.warn('[GraphOperations] Graph not found after retries:', updatedGraph.id);
      return null;
    };

    // Use async/await to handle the graph update
    (async () => {
      const existingGraph = await findGraph();
      if (!existingGraph) {
        return;
      }

      // Continue with graph update...
      // Validate all nodes have required data
      const hasInvalidNodes = updatedGraph.nodes.some(node => 
        !node?.id || !node?.data?.label || !node?.position?.x || !node?.position?.y
      );

      if (hasInvalidNodes) {
        console.error('[GraphOperations] Invalid node data in update:', 
          updatedGraph.nodes.map(n => ({
            id: n?.id,
            hasData: !!n?.data,
            hasLabel: !!n?.data?.label,
            hasPosition: !!(n?.position?.x && n?.position?.y)
          }))
        );
        return;
      }

      // Merge nodeData from existing graph
      const mergedNodeData = { ...existingGraph.nodeData };
      
      // Add any new nodeData
      updatedGraph.nodes.forEach(node => {
        if (!mergedNodeData[node.id]) {
          mergedNodeData[node.id] = {
            chat: [],
            notes: '',
            quiz: [],
            isLoadingDefinition: true
          };
        }
      });

      // Create merged graph
      const mergedGraph = {
        ...updatedGraph,
        nodeData: mergedNodeData
      };

      // Update graphs array first
      setGraphs(prevGraphs => {
        const currentGraphs = Array.isArray(prevGraphs) ? prevGraphs : [];
        return currentGraphs.map(g => 
          g.id === mergedGraph.id ? mergedGraph : g
        );
      });

      // Then update active graph if it matches
      setActiveGraph(prevGraph => {
        if (prevGraph?.id !== mergedGraph.id) return prevGraph;
        return mergedGraph;
      });
    })().catch(error => {
      console.error('[GraphOperations] Error updating graph:', error);
    });
  }, [graphs, setGraphs, setActiveGraph]);

  return {
    updateGraph
  };
}
