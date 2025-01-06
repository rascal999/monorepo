import { cytoscapeStylesheet } from './graphStyles';

// Merge base styles with dark mode styles
export const getDarkModeStyles = (baseStyles) => [
  ...baseStyles,
  {
    selector: 'node',
    style: {
      'background-color': '#6366f1',
      'border-color': '#4338ca',
      'border-width': 2,
      'label': 'data(label)',
      'color': '#fff',
      'text-valign': 'center',
      'text-halign': 'center',
      'width': 180,
      'height': 50,
      'font-size': 14,
      'font-weight': 500,
      'padding': '12px',
      'transition-property': 'background-color, border-color, width, height',
      'transition-duration': '0.3s',
      'text-outline-color': '#4338ca',
      'text-outline-width': 1,
      'border-opacity': 0.8,
      'shape': 'round-rectangle',
      'border-width': 3,
      'border-style': 'solid',
      'background-opacity': 0.95
    }
  },
  {
    selector: 'node:selected',
    style: {
      'background-color': '#818cf8',
      'border-color': '#4f46e5',
      'width': 190,
      'height': 55,
      'transition-timing-function': 'ease-out-cubic'
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 3,
      'line-color': '#94a3b8',
      'target-arrow-color': '#94a3b8',
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
      'line-color': '#475569',
      'target-arrow-color': '#475569',
      'width': 4,
      'transition-timing-function': 'ease-out-cubic'
    }
  }
];
