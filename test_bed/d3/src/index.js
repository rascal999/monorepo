import { data, getSelectedNode } from './data.js';
import { createGraph } from './graph/index.js';
import { initializeTheme } from './theme.js';
import { initializePanels, displayNodeDetails } from './panel.js';

// Initialize theme
initializeTheme();

// Initialize graph
const container = document.getElementById('graph');
createGraph(data, container);

// Initialize panels
initializePanels();

// Restore selected node if any
const selectedNode = getSelectedNode();
if (selectedNode) {
  displayNodeDetails(selectedNode);
}
