import cytoscape from 'cytoscape';
import { NodeSingular } from 'cytoscape';

type ColorScheme = {
  gradient: string;
  border: string;
  text: string;
};

export type ColorOption = 'blue' | 'green' | 'purple' | 'orange' | 'gray';

type ColorOptions = {
  [key in ColorOption]: ColorScheme;
};

export const defaultColors: ColorOptions = {
  blue: {
    gradient: '#F5F9FF #E3F2FD',
    border: '#90CAF9',
    text: '#1A237E'
  },
  green: {
    gradient: '#E8F5E9 #C8E6C9',
    border: '#81C784',
    text: '#1B5E20'
  },
  purple: {
    gradient: '#F3E5F5 #E1BEE7',
    border: '#CE93D8',
    text: '#311B92'
  },
  orange: {
    gradient: '#FFF3E0 #FFE0B2',
    border: '#FFB74D',
    text: '#E65100'
  },
  gray: {
    gradient: '#F5F5F5 #E0E0E0',
    border: '#9E9E9E',
    text: '#212121'
  }
};

export const colorOptions: ColorOption[] = ['blue', 'green', 'purple', 'orange', 'gray'];

export const GraphStyles: cytoscape.Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#E3F2FD',
      'background-gradient-direction': 'to-bottom',
      'background-gradient-stop-colors': 'data(properties.gradient)',
      'border-width': '1px',
      'border-color': 'data(properties.border)',
      'label': 'data(label)',
      'color': 'data(properties.text)',
      'text-valign': 'center',
      'text-halign': 'center',
      'font-size': '14px',
      'font-weight': 500,
      'text-max-width': '200px',
      'shape': 'round-rectangle',
      'width': 'label',
      'height': 'label',
      'padding': '16px',
      'text-wrap': 'wrap',
      'text-overflow-wrap': 'anywhere',
      'border-radius': '6px'
    } as cytoscape.Css.Node
  },
  {
    selector: 'node:hover',
    style: {
      'border-width': '2px'
    } as cytoscape.Css.Node
  },
  {
    selector: 'edge',
    style: {
      'width': '2px',
      'line-color': '#90CAF9',
      'target-arrow-color': '#90CAF9',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'label': 'data(label)',
      'font-size': '12px',
      'color': '#1565C0',
      'text-background-color': '#ffffff',
      'text-background-opacity': 1,
      'text-background-padding': '4px'
    } as cytoscape.Css.Edge
  },
  {
    selector: '.selected',
    style: {
      'border-width': '2px',
      'border-color': '#2196F3'
    } as cytoscape.Css.Node
  }
];
