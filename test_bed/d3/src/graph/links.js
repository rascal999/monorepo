import * as d3 from 'd3';

export function createLinks(g, links) {
  return g.append('g')
    .selectAll()
    .data(links)
    .join('line')
    .attr('class', 'link');
}

export function updateLinks(g, links) {
  return g.selectAll('line.link')
    .data(links)
    .join('line')
    .attr('class', 'link');
}

export function tickLinks(link) {
  link
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);
}
