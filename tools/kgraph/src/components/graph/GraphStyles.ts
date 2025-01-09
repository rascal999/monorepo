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
    gradient: '#0D47A1',
    border: '#1976D2',
    text: '#FFFFFF'
  },
  green: {
    gradient: '#1B5E20',
    border: '#388E3C',
    text: '#FFFFFF'
  },
  purple: {
    gradient: '#4A148C',
    border: '#7B1FA2',
    text: '#FFFFFF'
  },
  orange: {
    gradient: '#E65100',
    border: '#F57C00',
    text: '#FFFFFF'
  },
  gray: {
    gradient: '#212121',
    border: '#616161',
    text: '#FFFFFF'
  }
};

export const colorOptions: ColorOption[] = ['blue', 'green', 'purple', 'orange', 'gray'];

export const GraphStyles: cytoscape.Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'background-gradient-direction': 'to-bottom',
      'border-width': '2px',
      'label': 'data(label)',
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
      'border-radius': '6px',
      // Default blue theme
      'background-color': '#0D47A1',
      'background-gradient-stop-colors': '#0D47A1',
      'border-color': '#1976D2',
      'color': '#FFFFFF'
    } as cytoscape.Css.Node
  },
  {
    selector: 'node[?properties]',
    style: {
      'background-color': 'data(properties.gradient)',
      'background-gradient-stop-colors': 'data(properties.gradient)',
      'border-color': 'data(properties.border)',
      'color': '#FFFFFF'
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
