import { useEffect } from 'react';
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force';

export function useForceLayout(nodes, edges, width = 1000, height = 800, onPositionsCalculated) {
  // Run force simulation synchronously to calculate positions
  const calculatePositions = () => {
    if (!nodes.length) return;

    const simulation = forceSimulation()
      .force('charge', forceManyBody().strength(-500))
      .force('center', forceCenter(width / 2, height / 2))
      .force('collision', forceCollide(100))
      .force('link', forceLink().id(d => d.id).distance(200));

    // Create simulation nodes with current positions
    const simNodes = nodes.map(node => ({
      id: node.id,
      x: node.position?.x || width / 2,
      y: node.position?.y || height / 2
    }));

    // Convert edges to D3 format
    const simLinks = edges.map(edge => ({
      source: edge.data.source,
      target: edge.data.target
    }));

    // Set nodes and edges
    simulation.nodes(simNodes);
    simulation.force('link').links(simLinks);

    // Run simulation synchronously
    simulation.tick(300);

    // Get final positions
    const positions = simNodes.map(node => ({
      id: node.id,
      position: {
        x: Math.max(0, Math.min(width - 150, node.x)),
        y: Math.max(0, Math.min(height - 40, node.y))
      }
    }));

    // Stop simulation
    simulation.stop();

    return positions;
  };

  useEffect(() => {
    // Only calculate positions for nodes that have no position at all
    const nodesToPosition = nodes.filter(node => !node.position);

    if (nodesToPosition.length > 0) {
      console.log('Force layout: Calculating positions for new nodes:', nodesToPosition.length);
      const positions = calculatePositions();
      if (positions && onPositionsCalculated) {
        // Only update positions for nodes that need them
        const updatedPositions = positions
          .filter(pos => {
            const node = nodes.find(n => n.id === pos.id);
            return !node.position; // Only include nodes without positions
          });
        
        if (updatedPositions.length > 0) {
          console.log('Force layout: Updating positions for nodes:', updatedPositions.length);
          onPositionsCalculated(updatedPositions);
        }
      }
    }
  }, [nodes.length, width, height]); // Update when nodes or dimensions change
}
