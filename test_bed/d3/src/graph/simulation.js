import * as d3 from 'd3';

export function createSimulation(nodes, width, height) {
  const simulation = d3.forceSimulation()
    .nodes(nodes)
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width/2, height/2))
    // Add collision force to prevent overlap
    .force('collision', d3.forceCollide().radius(30))
    // Add x and y forces to maintain some structure
    .force('x', d3.forceX(width/2).strength(0.05))
    .force('y', d3.forceY(height/2).strength(0.05));

  // Configure link force
  const linkForce = d3.forceLink()
    .id(d => d.id)
    .distance(50)  // Shorter distance for tighter clustering
    .strength(1);  // Stronger links to keep children near parents

  simulation.force('link', linkForce);

  // Respect initial positions if they exist
  nodes.forEach(node => {
    if (typeof node.x === 'number' && typeof node.y === 'number') {
      // Fix position initially
      node.fx = node.x;
      node.fy = node.y;
      
      // Release after a short delay
      setTimeout(() => {
        node.fx = null;
        node.fy = null;
      }, 500);
    }
  });

  return simulation;
}

export function updateSimulation(simulation, nodes, links) {
  // Update nodes
  simulation.nodes(nodes);
  
  // Update links with proper references
  const linkForce = simulation.force('link');
  linkForce.links(links);
  
  // Restart simulation with higher alpha for more movement
  simulation.alpha(1).restart();
}

export function updateSimulationCenter(simulation, width, height) {
  simulation.force('center', d3.forceCenter(width/2, height/2));
  simulation.force('x', d3.forceX(width/2).strength(0.05));
  simulation.force('y', d3.forceY(height/2).strength(0.05));
  simulation.alpha(0.3).restart();
}
