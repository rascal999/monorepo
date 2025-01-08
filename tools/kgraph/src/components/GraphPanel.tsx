import React, { useRef, type FC, MutableRefObject } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch, useAppSelector } from '../store';
import { updateGraphViewport } from '../store/slices/graphSlice';
import GraphToolbar from './graph/GraphToolbar';
import type { Node, Graph, Viewport } from '../store/types';
import { useCytoscape } from '../hooks/useCytoscape';
import { useNodeSelection } from '../hooks/useNodeSelection';
import { useViewport } from '../hooks/useViewport';
import { useGraphData } from '../hooks/useGraphData';

interface GraphToolbarProps {
  currentGraph: Graph | null;
  cyRef: MutableRefObject<cytoscape.Core | null>;
  isInitializing: MutableRefObject<boolean>;
  onViewportUpdate: (viewport: Viewport) => void;
}

const defaultViewport = { zoom: 1, position: { x: 0, y: 0 } };

const GraphPanel: FC<{}> = (): JSX.Element => {
  const dispatch = useAppDispatch();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null) as MutableRefObject<cytoscape.Core | null>;
  const isInitializing = useRef<boolean>(false) as MutableRefObject<boolean>;
  const isFirstNode = useRef<boolean>(false) as MutableRefObject<boolean>;
  
  const currentGraph = useAppSelector(state => state.graph.currentGraph);
  const currentGraphRef = useRef<Graph | null>(null) as MutableRefObject<Graph | null>;
  const selectedNode = useAppSelector(state => state.node.selectedNode);
  const viewport = useAppSelector(state => state.graph.currentGraph?.viewport ?? defaultViewport);

  // Keep currentGraphRef in sync with currentGraph
  React.useEffect(() => {
    currentGraphRef.current = currentGraph;
    console.log('GraphPanel: Updated current graph ref', {
      hasGraph: Boolean(currentGraph),
      graphId: currentGraph?.id,
      nodeCount: currentGraph?.nodes?.length
    });
  }, [currentGraph]);

  // Initialize Cytoscape
  useCytoscape(containerRef, cyRef);

  // Set up node selection handling
  useNodeSelection(cyRef, currentGraphRef, selectedNode);

  // Set up viewport handling
  useViewport(cyRef, isInitializing);

  // Set up graph data management
  useGraphData(cyRef, currentGraph, isInitializing, isFirstNode);

  return (
    <div className="graph-panel">
      <GraphToolbar
        currentGraph={currentGraph}
        cyRef={cyRef}
        isInitializing={isInitializing}
        onViewportUpdate={(viewport) => dispatch(updateGraphViewport(viewport))}
      />
      <div ref={containerRef} className="cytoscape-container" />
    </div>
  );
};

export default GraphPanel;
