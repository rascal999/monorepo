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
    gradient: '#E3F2FD #BBDEFB',
    border: '#1976D2',
    text: '#0D47A1'
  },
  green: {
    gradient: '#E8F5E9 #C8E6C9',
    border: '#388E3C',
    text: '#1B5E20'
  },
  purple: {
    gradient: '#F3E5F5 #E1BEE7',
    border: '#7B1FA2',
    text: '#4A148C'
  },
  orange: {
    gradient: '#FFF3E0 #FFE0B2',
    border: '#F57C00',
    text: '#E65100'
  },
  gray: {
    gradient: '#F5F5F5 #E0E0E0',
    border: '#616161',
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
      'background-gradient-stop-colors': '#F5F9FF #E3F2FD',
      'border-width': '2px',
      'border-color': '#1976D2',
      'label': 'data(label)',
      'color': '#0D47A1',
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
    selector: 'node[?properties][?properties.gradient]',
    style: {
      'background-gradient-stop-colors': 'data(properties.gradient)'
    } as cytoscape.Css.Node
  },
  {
    selector: 'node[?properties][?properties.border]',
    style: {
      'border-color': 'data(properties.border)'
    } as cytoscape.Css.Node
  },
  {
    selector: 'node[?properties][?properties.text]',
    style: {
      'color': 'data(properties.text)'
    } as cytoscape.Css.Node
  },
  {
    selector: 'node:hover',
    style: {
      'border-width': '3px'
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
      'border-width': '3px'
    } as cytoscape.Css.Node
  }
];
