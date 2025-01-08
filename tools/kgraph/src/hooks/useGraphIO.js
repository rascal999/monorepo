import { useGraphValidation } from './useGraphValidation';

export function useGraphIO(graphs, setGraphs, setActiveGraph) {
  const { validateGraph } = useGraphValidation();

  const exportGraph = (graphId) => {
    console.log('[GraphOperations] Export requested for graph:', graphId);
    console.log('[GraphOperations] Available graphs:', graphs.map(g => ({
      id: g.id,
      title: g.title,
      nodesCount: g.nodes.length,
      firstNodeLabel: g.nodes[0]?.data?.label
    })));

    // Find the graph to export
    const graph = graphs.find(g => g.id === graphId);
    
    console.log('[GraphOperations] Found graph to export:', {
      graphId,
      title: graph?.title,
      nodesCount: graph?.nodes?.length,
      firstNodeLabel: graph?.nodes?.[0]?.data?.label,
      allNodes: graph?.nodes?.map(n => ({
        id: n.id,
        label: n.data?.label
      }))
    });
    if (!graph) {
      console.error('[GraphOperations] Graph not found for export:', graphId);
      return null;
    }

    // Get viewport data
    const viewportData = localStorage.getItem(`kgraph-viewport-${graphId}`);
    const viewport = viewportData ? JSON.parse(viewportData) : null;

    // Create export data structure
    const exportData = {
      version: '1.0',
      graph,
      viewport,
      exportDate: new Date().toISOString()
    };

    // Create and download file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    // Get initial node's label for filename
    const initialNode = graph.nodes[0];
    if (!initialNode?.data?.label) {
      console.error('[GraphOperations] Initial node label not found:', {
        initialNode,
        nodeData: initialNode?.data,
        allNodes: graph.nodes
      });
      return null;
    }
    
    console.log('[GraphOperations] Creating filename from label:', initialNode.data.label);
    const safeTitle = initialNode.data.label.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with single dash
      .replace(/^-+|-+$/g, ''); // Remove leading/trailing dashes
    a.download = `kgraph-${safeTitle}-${exportData.exportDate.split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const importGraph = async (file) => {
    console.log('[GraphOperations] Importing graph from file');
    
    try {
      const text = await file.text();
      const importData = JSON.parse(text);
      
      // Validate import data structure
      if (!importData.version || !importData.graph) {
        throw new Error('Invalid import data structure');
      }

      const graph = importData.graph;
      
      // Validate graph structure
      if (!validateGraph(graph)) {
        throw new Error('Invalid graph structure in import data');
      }

      // Generate new IDs to avoid conflicts
      const newGraphId = Date.now().toString();
      const idMap = new Map();
      
      // Update graph ID, title, and node IDs
      const initialNode = graph.nodes[0];
      const graphTitle = initialNode?.data?.label || 'Untitled Graph';
      // First create all node mappings
      const updatedNodes = graph.nodes.map(node => {
        const newId = (Date.now() + Math.random() * 1000).toString();
        idMap.set(node.id, newId);
        return { ...node, id: newId };
      });

      // Now we can safely get mapped IDs
      // Ensure we have a valid lastSelectedNodeId that exists in the graph
      const lastSelectedNodeId = graph.lastSelectedNodeId && graph.nodes.find(n => n.id === graph.lastSelectedNodeId)
        ? idMap.get(graph.lastSelectedNodeId)
        : idMap.get(graph.nodes[0].id);

      console.log('[GraphOperations] Setting lastSelectedNodeId:', {
        original: graph.lastSelectedNodeId,
        mapped: lastSelectedNodeId,
        firstNode: graph.nodes[0].id
      });

      const updatedGraph = {
        ...graph,
        id: parseInt(newGraphId),
        title: graphTitle,
        lastSelectedNodeId,
        nodes: updatedNodes,
        edges: graph.edges.map(edge => ({
          ...edge,
          id: (Date.now() + Math.random() * 1000).toString(),
          source: idMap.get(edge.source),
          target: idMap.get(edge.target)
        })),
        nodeData: Object.entries(graph.nodeData).reduce((acc, [oldId, data]) => {
          acc[idMap.get(oldId)] = data;
          return acc;
        }, {})
      };

      // Store viewport data if present
      if (importData.viewport) {
        localStorage.setItem(
          `kgraph-viewport-${newGraphId}`,
          JSON.stringify(importData.viewport)
        );
      }

      // Add graph to state and ensure node selection
      setGraphs(prevGraphs => [...prevGraphs, updatedGraph]);
      
      // Find the node to select
      const nodeToSelect = updatedNodes.find(n => n.id === lastSelectedNodeId) || updatedNodes[0];
      
      // Set active graph with explicit node selection
      setActiveGraph({
        ...updatedGraph,
        lastSelectedNodeId: nodeToSelect.id
      });

      return updatedGraph;
    } catch (error) {
      console.error('[GraphOperations] Import failed:', error);
      throw new Error(`Import failed: ${error.message}`);
    }
  };

  return {
    exportGraph,
    importGraph
  };
}
