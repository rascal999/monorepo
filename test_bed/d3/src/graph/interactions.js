import * as d3 from 'd3';

export function setupZoom(svg, g) {
  svg.call(d3.zoom()
    .extent([[0, 0], [svg.node().clientWidth, svg.node().clientHeight]])
    .scaleExtent([0.25, 4])
    .on('zoom', ({transform}) => g.attr('transform', transform)));
}

export function setupDrag(simulation) {
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

export function setupResizeHandler(container, svg, simulation) {
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
  return resizeObserver;
}
