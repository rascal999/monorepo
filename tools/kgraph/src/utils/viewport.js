// Validate viewport values
export const isValidViewport = (vp) => {
  return vp && 
    Number.isFinite(vp.x) && 
    Number.isFinite(vp.y) && 
    Number.isFinite(vp.zoom) &&
    !isNaN(vp.x) && 
    !isNaN(vp.y) && 
    !isNaN(vp.zoom);
};

// Get default viewport
export const getDefaultViewport = () => ({
  x: 0,
  y: 0,
  zoom: 1
});
