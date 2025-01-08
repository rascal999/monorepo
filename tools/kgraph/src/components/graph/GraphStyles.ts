import cytoscape from 'cytoscape';

export const GraphStyles: cytoscape.Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#666',
      'label': 'data(label)',
      'text-valign': 'center',
      'text-halign': 'center',
      'width': '30px',
      'height': '30px'
    } as cytoscape.Css.Node
  },
  {
    selector: 'edge',
    style: {
      'width': '2px',
      'line-color': '#ccc',
      'target-arrow-color': '#ccc',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'label': 'data(label)'
    } as cytoscape.Css.Edge
  },
  {
    selector: '.selected',
    style: {
      'background-color': '#007bff',
      'line-color': '#007bff', 
      'target-arrow-color': '#007bff'
    } as cytoscape.Css.Node
  }
];
