import * as d3 from 'd3';
import { displayNodeDetails } from '../panel.js';
import { setSelectedNode, getSelectedNode } from '../data.js';
import { setupDrag } from './interactions.js';

export function createNodes(g, nodes, simulation) {
  const nodeGroup = g.append('g')
    .selectAll()
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .call(setupDrag(simulation))
    .on('click', (event, d) => {
      console.log('Clicked node:', d);
      setSelectedNode(d);
      displayNodeDetails(d);
      
      // Highlight selected node
      g.selectAll('circle')
        .style('fill', n => n === d ? '#ff7f0e' : '#1f77b4');
    });

  // Add circles for nodes
  nodeGroup.append('circle')
    .attr('r', 5)
    .style('fill', d => d === getSelectedNode() ? '#ff7f0e' : '#1f77b4');

  // Add labels
  nodeGroup.append('text')
    .text(d => d.name)
    .attr('x', 8)
    .attr('y', '0.31em');

  return nodeGroup;
}

export function updateNodes(g, nodes, simulation) {
  // Update nodes
  const node = g.selectAll('g.node')
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .call(setupDrag(simulation))
    .on('click', (event, d) => {
      console.log('Clicked node:', d);
      setSelectedNode(d);
      displayNodeDetails(d);
      
      // Highlight selected node
      g.selectAll('circle')
        .style('fill', n => n === d ? '#ff7f0e' : '#1f77b4');
    });

  // Ensure all nodes have circles and labels
  node.selectAll('circle').remove();
  node.selectAll('text').remove();

  node.append('circle')
    .attr('r', 5)
    .style('fill', d => d === getSelectedNode() ? '#ff7f0e' : '#1f77b4');

  node.append('text')
    .text(d => d.name)
    .attr('x', 8)
    .attr('y', '0.31em');

  return node;
}

export function tickNodes(node) {
  node.attr('transform', d => `translate(${d.x},${d.y})`);
}
