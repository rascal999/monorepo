import { useEffect, RefObject, MutableRefObject } from 'react';
import cytoscape from 'cytoscape';
import { GraphStyles } from '../components/graph/GraphStyles';
import { NodeSingular } from 'cytoscape';

type ContextMenuHandler = (node: NodeSingular, event: MouseEvent) => void;

export const useCytoscape = (
  containerRef: RefObject<HTMLDivElement>,
  cyRef: MutableRefObject<cytoscape.Core | null>,
  onContextMenu?: ContextMenuHandler
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
      wheelSensitivity: 0.2,
      boxSelectionEnabled: false,
      autoungrabify: false,
      autounselectify: true
    });

    cyRef.current = cy;

    // Add right-click handler for nodes
    if (onContextMenu) {
      cy.on('cxttap', 'node', (event) => {
        const node = event.target;
        onContextMenu(node, event.originalEvent as MouseEvent);
      });
    }

    return () => {
      cy.destroy();
    };
  }, [onContextMenu]);
};
