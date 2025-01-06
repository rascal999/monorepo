export const cytoscapeStylesheet = [
  {
    selector: 'node',
    style: {
      'background-color': '#FCE7F3', // pink-100
      'border-color': '#F472B6',     // pink-400
      'border-width': 2,
      'label': 'data(label)',
      'color': '#1A1A1A',
      'text-valign': 'center',
      'text-halign': 'center',
      'width': 180,
      'height': 50,
      'font-size': 14,
      'font-weight': 500,
      'padding': '12px',
      'transition-property': 'background-color, border-color, width, height',
      'transition-duration': '0.3s',
      'text-outline-color': '#FCE7F3',
      'text-outline-width': 1,
      'border-opacity': 0.8,
      'shape': 'round-rectangle',
      // Replace shadow with border effects for depth
      'border-width': 3,
      'border-style': 'solid',
      'background-opacity': 0.95
    }
  },
  {
    selector: 'node:selected',
    style: {
      'background-color': '#F9A8D4', // pink-300
      'border-color': '#EC4899',     // pink-500
      'width': 190,
      'height': 55,
      'transition-timing-function': 'ease-out-cubic',
      'border-width': 4,
      'background-opacity': 1
    }
  },
  {
    selector: 'node.loading',
    style: {
      'background-opacity': 0.5,
      'border-style': 'dashed'
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 3,
      'line-color': '#F472B6',
      'target-arrow-color': '#F472B6',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 1.5,
      'transition-property': 'line-color, target-arrow-color, width',
      'transition-duration': '0.3s',
      'opacity': 0.8
    }
  },
  {
    selector: 'edge:selected',
    style: {
      'line-color': '#EC4899',
      'target-arrow-color': '#EC4899',
      'width': 4,
      'transition-timing-function': 'ease-out-cubic'
    }
  }
];
