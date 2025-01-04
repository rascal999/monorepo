import { useState } from 'react';

export function useViewportState(initialViewport) {
  const [viewport, setViewport] = useState(initialViewport);

  const updateViewport = (newViewport) => {
    // Validate viewport before updating
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
    setViewport({
      x: 0,
      y: 0,
      zoom: 1
    });
  };

  return {
    viewport,
    updateViewport,
    resetViewport
  };
}
