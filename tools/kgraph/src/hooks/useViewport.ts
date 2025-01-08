import { useEffect, RefObject, MutableRefObject } from 'react';
import cytoscape from 'cytoscape';
import { useAppDispatch } from '../store';
import { updateGraphViewport } from '../store/slices/graphSlice';

export const useViewport = (
  cyRef: RefObject<cytoscape.Core | null>,
  isInitializing: MutableRefObject<boolean>
) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    let viewportUpdateTimeout: NodeJS.Timeout;
    const handleViewportChange = () => {
      if (isInitializing.current) return;
      
      clearTimeout(viewportUpdateTimeout);
      viewportUpdateTimeout = setTimeout(() => {
        if (!cyRef.current) return;
        dispatch(updateGraphViewport({
          zoom: cyRef.current.zoom(),
          position: {
            x: -cyRef.current.pan().x,
            y: -cyRef.current.pan().y
          }
        }));
      }, 100);
    };

    cy.on('viewport', handleViewportChange);
    return () => {
      cy.off('viewport', handleViewportChange);
      clearTimeout(viewportUpdateTimeout);
    };
  }, [cyRef.current]);
};
