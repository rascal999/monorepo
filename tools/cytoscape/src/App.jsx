import { useState, useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import styled from '@emotion/styled';
import './index.css';

// Sample graph data in Cytoscape format
const graph1 = [
  // Nodes
  { data: { id: '1', label: 'Graph 1 - Node 1' }, position: { x: 250, y: 100 } },
  { data: { id: '2', label: 'Graph 1 - Node 2' }, position: { x: 250, y: 200 } },
  // Edges
  { data: { id: 'e1-2', source: '1', target: '2' } }
];

const graph2 = [
  // Nodes
  { data: { id: '1', label: 'Graph 2 - Node 1' }, position: { x: 250, y: 50 } },
  { data: { id: '2', label: 'Graph 2 - Node 2' }, position: { x: 150, y: 150 } },
  { data: { id: '3', label: 'Graph 2 - Node 3' }, position: { x: 350, y: 150 } },
  // Edges
  { data: { id: 'e1-2', source: '1', target: '2' } },
  { data: { id: 'e1-3', source: '1', target: '3' } }
];

const graph3 = [
  // Nodes
  { data: { id: '1', label: 'Graph 3 - Node 1' }, position: { x: 250, y: 100 } },
  { data: { id: '2', label: 'Graph 3 - Node 2' }, position: { x: 100, y: 200 } },
  { data: { id: '3', label: 'Graph 3 - Node 3' }, position: { x: 250, y: 200 } },
  { data: { id: '4', label: 'Graph 3 - Node 4' }, position: { x: 400, y: 200 } },
  // Edges
  { data: { id: 'e1-2', source: '1', target: '2' } },
  { data: { id: 'e1-3', source: '1', target: '3' } },
  { data: { id: 'e1-4', source: '1', target: '4' } }
];

const graphs = {
  graph1,
  graph2,
  graph3,
};

// Cytoscape styles
const cytoscapeStylesheet = [
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
      'shadow-blur': 10,
      'shadow-color': 'rgba(0, 0, 0, 0.2)',
      'shadow-offset-x': 0,
      'shadow-offset-y': 4,
      'shadow-opacity': 0.8,
      'border-opacity': 0.8,
      'shape': 'round-rectangle'
    }
  },
  {
    selector: 'node:hover',
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
      'target-arrow-shape': 'vee',
      'curve-style': 'straight',
      'arrow-scale': 1.5,
      'transition-property': 'line-color, target-arrow-color, width',
      'transition-duration': '0.3s',
      'opacity': 0.8,
      'line-style': 'solid',
      'target-distance-from-node': 0,
      'source-distance-from-node': 0,
      'mid-source-position': 'middle middle',
      'mid-target-position': 'middle middle'
    }
  },
  {
    selector: 'edge:hover',
    style: {
      'line-color': '#475569',
      'target-arrow-color': '#475569',
      'width': 4,
      'transition-timing-function': 'ease-out-cubic'
    }
  }
];

// Styled components
const Container = styled.div`
  display: flex;
  width: 100vw;
  height: 100vh;
`;

const LeftPanel = styled.div`
  width: 200px;
  padding: 20px;
  background-color: #f8f9fa;
  border-right: 1px solid #dee2e6;
`;

const GraphButton = styled.button`
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  background-color: ${props => props.active ? '#0d6efd' : '#fff'};
  color: ${props => props.active ? '#fff' : '#000'};
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background-color: ${props => props.active ? '#0b5ed7' : '#f8f9fa'};
  }
`;

const GraphContainer = styled.div`
  flex: 1;
  height: 100%;
`;

function Graph({ selectedGraph }) {
  const cyRef = useRef(null);

  const handleInit = (cy) => {
    cyRef.current = cy;

    // Load stored viewport
    const storedViewport = localStorage.getItem(`viewport-${selectedGraph}`);
    if (storedViewport) {
      const { zoom, pan } = JSON.parse(storedViewport);
      cy.zoom(zoom);
      cy.pan(pan);
    } else {
      cy.fit(undefined, 50);
    }

    // Add viewport change listener
    const handleViewportChange = () => {
      const viewport = {
        zoom: cy.zoom(),
        pan: cy.pan()
      };
      localStorage.setItem(`viewport-${selectedGraph}`, JSON.stringify(viewport));
    };

    cy.on('viewport', handleViewportChange);
  };

  useEffect(() => {
    return () => {
      if (cyRef.current) {
        cyRef.current.removeAllListeners();
      }
    };
  }, [selectedGraph]);

  return (
    <CytoscapeComponent
      elements={graphs[selectedGraph]}
      style={{ width: '100%', height: '100%' }}
      stylesheet={cytoscapeStylesheet}
      cy={handleInit}
      minZoom={0.1}
      maxZoom={4}
    />
  );
}

function App() {
  const [selectedGraph, setSelectedGraph] = useState('graph1');

  return (
    <Container>
      <LeftPanel>
        <GraphButton
          active={selectedGraph === 'graph1'}
          onClick={() => setSelectedGraph('graph1')}
        >
          Graph 1
        </GraphButton>
        <GraphButton
          active={selectedGraph === 'graph2'}
          onClick={() => setSelectedGraph('graph2')}
        >
          Graph 2
        </GraphButton>
        <GraphButton
          active={selectedGraph === 'graph3'}
          onClick={() => setSelectedGraph('graph3')}
        >
          Graph 3
        </GraphButton>
      </LeftPanel>
      <GraphContainer>
        <Graph key={selectedGraph} selectedGraph={selectedGraph} />
      </GraphContainer>
    </Container>
  );
}

export default App;
