import { useState, useEffect, useRef } from 'react';
import { isValidViewport, getDefaultViewport } from '../utils/viewport';

export function useViewportState(graphId) {
  const prevGraphIdRef = useRef(graphId);

  // Initialize viewport state with saved or default
  const [viewport, setViewport] = useState(() => {
    if (!graphId) return getDefaultViewport();

    try {
      const saved = localStorage.getItem(`kgraph-viewport-${graphId}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (isValidViewport(parsed)) {
          console.log('[ViewportState] Loaded initial viewport:', {
            graphId,
            viewport: parsed
          });
          return parsed;
        }
      }
    } catch (e) {
      console.error('[ViewportState] Error loading initial viewport:', e);
    }

    return getDefaultViewport();
  });

  // Handle graph changes
  useEffect(() => {
    if (graphId === prevGraphIdRef.current) return;

    console.log('[ViewportState] Graph changed:', {
      from: prevGraphIdRef.current,
      to: graphId
    });

    // Try to load saved viewport for new graph
    if (graphId) {
      try {
        const saved = localStorage.getItem(`kgraph-viewport-${graphId}`);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (isValidViewport(parsed)) {
            console.log('[ViewportState] Loading saved viewport:', {
              graphId,
              viewport: parsed
            });
            setViewport(parsed);
          } else {
            console.log('[ViewportState] Invalid saved viewport, using default');
            setViewport(getDefaultViewport());
          }
        } else {
          console.log('[ViewportState] No saved viewport, using default');
          setViewport(getDefaultViewport());
        }
      } catch (e) {
        console.error('[ViewportState] Error loading viewport:', e);
        setViewport(getDefaultViewport());
      }
    }

    prevGraphIdRef.current = graphId;
  }, [graphId]);

  // Update viewport
  const updateViewport = (newViewport) => {
    if (!graphId || !isValidViewport(newViewport)) return;

    // Skip if viewport hasn't changed
    if (viewport && 
        viewport.x === newViewport.x && 
        viewport.y === newViewport.y && 
        viewport.zoom === newViewport.zoom) {
      return;
    }

    setViewport(newViewport);

    // Save to localStorage
    try {
      localStorage.setItem(`kgraph-viewport-${graphId}`, JSON.stringify(newViewport));
    } catch (e) {
      console.error('[ViewportState] Error saving viewport:', e);
    }
  };

  return {
    viewport,
    updateViewport
  };
}
