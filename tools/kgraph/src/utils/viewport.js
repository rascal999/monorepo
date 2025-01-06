// Default viewport values - centered in a typical view
const DEFAULT_VIEWPORT = {
  x: 0,
  y: 0,
  zoom: 1
};

// Validate viewport values
export const isValidViewport = (vp) => {
  if (!vp) return false;
  
  const { x, y, zoom } = vp;
  
  // Check for required properties
  if (x === undefined || y === undefined || zoom === undefined) {
    return false;
  }
  
  // Validate numeric values
  if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(zoom)) {
    return false;
  }
  
  // Check for NaN values
  if (isNaN(x) || isNaN(y) || isNaN(zoom)) {
    return false;
  }
  
  // Ensure zoom is positive
  if (zoom <= 0) {
    return false;
  }
  
  return true;
};

// Get default viewport
export const getDefaultViewport = () => ({ ...DEFAULT_VIEWPORT });

// Parse viewport from storage
export const parseViewport = (data) => {
  try {
    const parsed = JSON.parse(data);
    return isValidViewport(parsed) ? parsed : getDefaultViewport();
  } catch (e) {
    console.error('Error parsing viewport:', e);
    return getDefaultViewport();
  }
};
