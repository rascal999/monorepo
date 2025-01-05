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
      .force('link', forceLink().distance(200));

    // Create simulation nodes with current positions
    const simNodes = nodes.map(node => ({
      ...node,
      x: node.position.x,
      y: node.position.y,
      id: node.id
    }));

    // Set nodes and edges
    simulation.nodes(simNodes);
    simulation.force('link').links(edges);

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
    // Only calculate positions for new nodes
    const newNodes = nodes.filter(node => !node.position || (node.position.x === 0 && node.position.y === 0));
    if (newNodes.length > 0) {
      const positions = calculatePositions();
      if (positions && onPositionsCalculated) {
        onPositionsCalculated(positions);
      }
    }
  }, [nodes.length]); // Only run when number of nodes changes
}
