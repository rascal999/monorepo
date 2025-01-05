/**
 * Calculate position for a new node based on parent position and child count
 */
export function generateNodePosition(parentPosition, childCount) {
  // Fixed radius for consistent spacing
  const radius = 250;
  
  // Calculate angle based on child count (30 degree spacing)
  const angle = (childCount * Math.PI / 6) + (Math.PI / 6);
  
  // Calculate offset using polar coordinates
  const x = Math.cos(angle) * radius;
  const y = Math.sin(angle) * radius;
  
  // Add random jitter to prevent exact overlaps
  const jitter = 20;
  const jitterX = (Math.random() - 0.5) * jitter;
  const jitterY = (Math.random() - 0.5) * jitter;
  
  return {
    x: parentPosition.x + x + jitterX,
    y: parentPosition.y + y + jitterY
  };
}

/**
 * Calculate initial positions for a set of nodes
 */
export function layoutNodes(nodes, edges) {
  if (!nodes.length) return nodes;
  
  // Find root nodes (nodes with no incoming edges)
  const rootNodes = nodes.filter(node => 
    !edges.some(edge => edge.target === node.id)
  );
  
  // Start from center if no root nodes
  if (!rootNodes.length) {
    const centerNode = nodes[0];
    centerNode.position = { x: 500, y: 300 };
    return layoutFromNode(centerNode, nodes, edges);
  }
  
  // Layout from each root node
  rootNodes.forEach((root, i) => {
    const angle = (i * Math.PI * 2) / rootNodes.length;
    root.position = {
      x: 500 + Math.cos(angle) * 200,
      y: 300 + Math.sin(angle) * 200
    };
    layoutFromNode(root, nodes, edges);
  });
  
  return nodes;
}

function layoutFromNode(node, nodes, edges) {
  // Get child nodes
  const childEdges = edges.filter(edge => edge.source === node.id);
  const children = childEdges.map(edge => 
    nodes.find(n => n.id === edge.target)
  ).filter(Boolean);
  
  // Position each child
  children.forEach((child, i) => {
    if (!child.position) {
      child.position = generateNodePosition(node.position, i);
      // Recursively layout children
      layoutFromNode(child, nodes, edges);
    }
  });
  
  return nodes;
}
