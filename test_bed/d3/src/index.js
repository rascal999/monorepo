import * as d3 from 'd3';
import { data } from './data.js';
import { initializePanels } from './panel.js';
import { createGraph } from './graph.js';
import { initializeTheme } from './theme.js';

// Initialize theme system
initializeTheme();

// Initialize panels with resizers
initializePanels();

// Initialize graph
const container = document.getElementById('graph-container');
const graph = createGraph(data, container);

// Handle window resize
window.addEventListener('resize', () => {
  const width = container.clientWidth;
  const height = container.clientHeight;
  graph.svg.attr('viewBox', [0, 0, width, height]);
  graph.simulation.force('center', d3.forceCenter(width/2, height/2));
  graph.simulation.alpha(0.3).restart();
});
