// Initialize graph data from localStorage or use default
let graphData = {
  nodes: [
    { id: 1, name: "Node 1" },
    { id: 2, name: "Node 2" },
    { id: 3, name: "Node 3" },
    { id: 4, name: "Node 4" },
    { id: 5, name: "Node 5" }
  ],
  links: [
    { source: 1, target: 2 },
    { source: 2, target: 3 },
    { source: 3, target: 4 },
    { source: 4, target: 5 },
    { source: 1, target: 5 }
  ]
};

try {
  const savedData = JSON.parse(localStorage.getItem('graphData'));
  if (savedData) {
    // Ensure links use IDs instead of node references
    savedData.links = savedData.links.map(link => ({
      source: typeof link.source === 'object' ? link.source.id : link.source,
      target: typeof link.target === 'object' ? link.target.id : link.target
    }));
    graphData = savedData;
  }
} catch (e) {
  console.error('Error loading graph data:', e);
}

// Keep track of the highest node ID
let maxNodeId = Math.max(...graphData.nodes.map(n => n.id));

// Track currently selected node
let selectedNode = null;

// Try to restore last selected node
const lastSelectedId = localStorage.getItem('selectedNodeId');
if (lastSelectedId) {
  selectedNode = graphData.nodes.find(n => n.id === parseInt(lastSelectedId));
}

export function setSelectedNode(node) {
  selectedNode = node;
  // Save selected node ID
  if (node) {
    localStorage.setItem('selectedNodeId', node.id);
  } else {
    localStorage.removeItem('selectedNodeId');
  }
}

export function getSelectedNode() {
  return selectedNode;
}

export function addNode(name) {
  const newId = ++maxNodeId;
  
  // Create new node with offset from parent if it exists
  const newNode = { 
    id: newId, 
    name
  };
  
  // If parent exists, add position with offset
  if (selectedNode) {
    // Generate random angle and distance for offset
    const angle = Math.random() * 2 * Math.PI;
    const distance = 50; // Fixed distance for consistent spacing
    
    newNode.x = (selectedNode.x || 0) + Math.cos(angle) * distance;
    newNode.y = (selectedNode.y || 0) + Math.sin(angle) * distance;
  }
  
  graphData.nodes.push(newNode);
  
  // If there's a selected node, create a link from it to the new node
  if (selectedNode) {
    graphData.links.push({
      source: selectedNode.id,
      target: newId
    });
  }
  
  // Save graph structure
  localStorage.setItem('graphData', JSON.stringify(graphData));
  
  return newNode;
}

export function getData() {
  return graphData;
}

// Export initial data for backwards compatibility
export const data = graphData;
