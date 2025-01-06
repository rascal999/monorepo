import { useState, useEffect, useRef } from 'react';
import { isValidViewport, getDefaultViewport } from '../utils/viewport';

export function useViewportState(graphId) {
  const prevGraphIdRef = useRef(graphId);

  // Initialize viewport state
  const [viewport, setViewport] = useState(() => {
    if (!graphId) return getDefaultViewport();

    // Try to load saved viewport
    try {
      const saved = localStorage.getItem(`kgraph-viewport-${graphId}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (isValidViewport(parsed)) {
          console.log('[ViewportState] Loading initial viewport', { graphId, viewport: parsed });
          return parsed;
        }
      }
    } catch (e) {
      console.error('[ViewportState] Error loading viewport:', e);
    }

    return getDefaultViewport();
  });

  // Save viewport when it changes
  useEffect(() => {
    if (!graphId || !viewport || !isValidViewport(viewport)) return;

    const storageKey = `kgraph-viewport-${graphId}`;
    try {
      localStorage.setItem(storageKey, JSON.stringify(viewport));
      console.warn('[ViewportState] Viewport auto-saved', {
        graphId,
        storageKey,
        viewport
      });
    } catch (e) {
      console.error('[ViewportState] Error auto-saving viewport:', e);
    }
  }, [graphId, viewport]);

  // Handle graph changes
  useEffect(() => {
    if (graphId === prevGraphIdRef.current) return;

    console.warn('[ViewportState] Graph changed', {
      from: prevGraphIdRef.current,
      to: graphId
    });

    // Load viewport for new graph
    if (graphId) {
      const storageKey = `kgraph-viewport-${graphId}`;
      const saved = localStorage.getItem(storageKey);
      console.warn('[ViewportState] Attempting to load viewport', {
        graphId,
        storageKey,
        savedData: saved
      });

      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (isValidViewport(parsed)) {
            console.warn('[ViewportState] Loading saved viewport', {
              graphId,
              viewport: parsed
            });
            setViewport(parsed);
          } else {
            console.warn('[ViewportState] Invalid saved viewport, using default');
            setViewport(getDefaultViewport());
          }
        } catch (e) {
          console.error('[ViewportState] Error loading viewport:', e);
          setViewport(getDefaultViewport());
        }
      } else {
        console.warn('[ViewportState] No saved viewport, using default');
        setViewport(getDefaultViewport());
      }
    }

    prevGraphIdRef.current = graphId;
  }, [graphId]); // Only depend on graphId changes

  // Save viewport on window unload
  useEffect(() => {
    const handleUnload = () => {
      if (graphId && viewport && isValidViewport(viewport)) {
        console.log('[ViewportState] Saving viewport on unload', { graphId, viewport });
        localStorage.setItem(`kgraph-viewport-${graphId}`, JSON.stringify(viewport));
      }
    };

    window.addEventListener('beforeunload', handleUnload);
    return () => window.removeEventListener('beforeunload', handleUnload);
  }, [graphId, viewport]);

  // Update viewport
  const updateViewport = (newViewport) => {
    if (!graphId || !isValidViewport(newViewport)) {
      console.warn('[ViewportState] Invalid viewport update', {
        graphId,
        newViewport,
        isValid: isValidViewport(newViewport)
      });
      return;
    }

    // Check if viewport actually changed
    if (viewport && 
        viewport.x === newViewport.x && 
        viewport.y === newViewport.y && 
        viewport.zoom === newViewport.zoom) {
      return;
    }
    
    console.warn('[ViewportState] Updating viewport', {
      graphId,
      from: viewport,
      to: newViewport
    });
    
    setViewport(newViewport);
    
    // Debounce localStorage save
    const storageKey = `kgraph-viewport-${graphId}`;
    const saveToStorage = () => {
      try {
        localStorage.setItem(storageKey, JSON.stringify(newViewport));
        console.warn('[ViewportState] Viewport saved', {
          graphId,
          storageKey,
          viewport: newViewport
        });
      } catch (e) {
        console.error('[ViewportState] Error saving viewport:', e);
      }
    };

    // Use requestAnimationFrame to debounce saves
    requestAnimationFrame(saveToStorage);
  };

  return {
    viewport,
    updateViewport
  };
}
