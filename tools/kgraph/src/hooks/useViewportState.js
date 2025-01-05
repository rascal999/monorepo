import { useState, useEffect } from 'react';

export function useViewportState() {
  // Initialize viewport state
  const [viewport, setViewport] = useState(() => {
    try {
      const saved = localStorage.getItem('kgraph-viewport');
      const parsed = saved ? JSON.parse(saved) : null;
      if (parsed && 
          Number.isFinite(parsed.x) && 
          Number.isFinite(parsed.y) && 
          Number.isFinite(parsed.zoom) &&
          !isNaN(parsed.x) && 
          !isNaN(parsed.y) && 
          !isNaN(parsed.zoom)) {
        return parsed;
      }
    } catch (e) {
      console.error('Error parsing viewport:', e);
    }
    return { x: 0, y: 0, zoom: 1 };
  });

  // Persist viewport
  useEffect(() => {
    if (viewport) {
      localStorage.setItem('kgraph-viewport', JSON.stringify(viewport));
    }
  }, [viewport]);

  const updateViewport = (newViewport) => {
    if (newViewport && 
        Number.isFinite(newViewport.x) && 
        Number.isFinite(newViewport.y) && 
        Number.isFinite(newViewport.zoom) &&
        !isNaN(newViewport.x) && 
        !isNaN(newViewport.y) && 
        !isNaN(newViewport.zoom)) {
      setViewport(newViewport);
    }
  };

  const resetViewport = () => {
    setViewport({ x: 0, y: 0, zoom: 1 });
  };

  return {
    viewport,
    updateViewport,
    resetViewport
  };
}
