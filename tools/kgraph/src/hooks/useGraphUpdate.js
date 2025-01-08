import { useEffect, useRef, useCallback } from 'react';

export function useGraphUpdate(updateFn) {
  // Track updates
  const updateTimeoutRef = useRef(null);
  const lastUpdateRef = useRef(null);
  const UPDATE_THROTTLE = 16; // ~60fps

  // Throttled update function
  const throttledUpdate = useCallback((...args) => {
    const now = Date.now();
    const timeSinceLastUpdate = now - (lastUpdateRef.current || 0);

    // Clear any pending update
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // If we're updating too frequently, throttle
    if (timeSinceLastUpdate < UPDATE_THROTTLE) {
      updateTimeoutRef.current = setTimeout(() => {
        if (updateFn) {
          updateFn(...args);
          lastUpdateRef.current = Date.now();
        }
      }, UPDATE_THROTTLE - timeSinceLastUpdate);
      return;
    }

    // Otherwise update immediately
    if (updateFn) {
      updateFn(...args);
      lastUpdateRef.current = now;
    }
  }, [updateFn]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, []);

  return throttledUpdate;
}
