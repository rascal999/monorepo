import * as d3 from 'd3';
import { displayNodeDetails } from './panel.js';

export function createGraph(data, container) {
  const width = container.clientWidth;
  const height = container.clientHeight;

  const svg = d3.select('#graph')
    .append('svg')
    .attr('viewBox', [0, 0, width, height]);

  const g = svg.append('g');

  svg.call(d3.zoom()
    .extent([[0, 0], [width, height]])
    .scaleExtent([0.25, 4])
    .on('zoom', ({transform}) => g.attr('transform', transform)));

  const simulation = d3.forceSimulation()
    .nodes(data.nodes)
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width/2, height/2))
    .on('tick', ticked);

  simulation.force('link', d3.forceLink(data.links)
    .id(d => d.id));

  const link = g.append('g')
    .selectAll()
    .data(data.links)
    .join('line')
    .attr('class', 'link');

  const node = g.append('g')
    .selectAll()
    .data(data.nodes)
    .join('g')
    .attr('class', 'node')
    .call(drag(simulation))
    .on('click', (event, d) => {
      console.log('Clicked node:', d);
      displayNodeDetails(d);
    });

  node.append('circle')
    .attr('r', 5)
    .style('fill', '#1f77b4');

  node.append('text')
    .text(d => d.name)
    .attr('x', 8)
    .attr('y', '0.31em');

  function ticked() {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    node.attr('transform', d => `translate(${d.x},${d.y})`);
  }

  function drag(simulation) {
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }
    
    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
    
    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  }

  // Handle container resize
  const resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const width = entry.contentRect.width;
      const height = entry.contentRect.height;
      svg.attr('viewBox', [0, 0, width, height]);
      simulation.force('center', d3.forceCenter(width/2, height/2));
      simulation.alpha(0.3).restart();
    }
  });

  resizeObserver.observe(container);

  return {
    simulation,
    svg,
    container
  };
}
