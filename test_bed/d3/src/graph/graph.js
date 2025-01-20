import * as d3 from 'd3';
import { getData } from '../data.js';
import { createSimulation, updateSimulation } from './simulation.js';
import { setupZoom, setupResizeHandler } from './interactions.js';
import { createNodes, updateNodes, tickNodes } from './nodes.js';
import { createLinks, updateLinks, tickLinks } from './links.js';

let currentSimulation;
let currentG;
let currentNodes;
let currentLinks;

export function createGraph(data, container) {
  currentSimulation = null;
  currentG = null;
  currentNodes = null;
  currentLinks = null;

  const width = container.clientWidth;
  const height = container.clientHeight;

  const svg = d3.select('#graph')
    .append('svg')
    .attr('viewBox', [0, 0, width, height]);

  currentG = svg.append('g');

  // Setup zoom
  setupZoom(svg, currentG);

  // Create simulation
  currentSimulation = createSimulation(data.nodes, width, height);

  // Create links and nodes
  currentLinks = createLinks(currentG, data.links);
  currentNodes = createNodes(currentG, data.nodes, currentSimulation);

  // Setup simulation links
  currentSimulation.force('link').links(data.links);

  // Setup tick handler
  currentSimulation.on('tick', () => {
    tickLinks(currentLinks);
    tickNodes(currentNodes);
  });

  // Setup resize handler
  setupResizeHandler(container, svg, currentSimulation);

  return {
    simulation: currentSimulation,
    svg,
    container
  };
}

export function updateGraph() {
  if (!currentSimulation || !currentG) return;
  
  const data = getData();
  
  // Update links and nodes
  currentLinks = updateLinks(currentG, data.links);
  currentNodes = updateNodes(currentG, data.nodes, currentSimulation);
  
  // Update simulation
  updateSimulation(currentSimulation, data.nodes, data.links);
}
