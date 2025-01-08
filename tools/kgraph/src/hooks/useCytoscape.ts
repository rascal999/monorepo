import { useEffect, RefObject, MutableRefObject } from 'react';
import cytoscape from 'cytoscape';
import { GraphStyles } from '../components/graph/GraphStyles';

export const useCytoscape = (
  containerRef: RefObject<HTMLDivElement>,
  cyRef: MutableRefObject<cytoscape.Core | null>
) => {
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      minZoom: 0.1,
      maxZoom: 3,
      style: GraphStyles,
      layout: {
        name: 'grid'
      },
      userPanningEnabled: true,
      userZoomingEnabled: true,
      boxSelectionEnabled: false,
      autoungrabify: false,
      autounselectify: true
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, []);
};
