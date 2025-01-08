import React, { useEffect } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch } from '../../store';
import { startDrag, endDrag } from '../../store/slices/appSlice';

interface GraphEventHandlersProps {
  cyRef: React.MutableRefObject<cytoscape.Core | null>;
}

const GraphEventHandlers: React.FC<GraphEventHandlersProps> = ({ cyRef }) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (!cyRef.current) return;

    const cy = cyRef.current;

    // Handle grab/free events for dragging
    cy.on('grab', 'node', (evt) => {
      const node = evt.target;
      dispatch(startDrag(node.id()));
    });

    cy.on('free', 'node', () => {
      dispatch(endDrag());
    });

    return () => {
      cy.removeListener('grab');
      cy.removeListener('free');
    };
  }, [cyRef, dispatch]);

  return null;
};

export default GraphEventHandlers;
