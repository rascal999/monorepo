import { useEffect, useRef, useCallback } from 'react';

export function useGraphUpdate(updateFn) {
  // Track updates
  const updateTimeoutRef = useRef(null);
  const lastUpdateRef = useRef(null);
  const pendingUpdateRef = useRef(null);
  const UPDATE_THROTTLE = 100; // Increase throttle time

  // Throttled update function
  const throttledUpdate = useCallback((...args) => {
    const now = Date.now();
    const timeSinceLastUpdate = now - (lastUpdateRef.current || 0);

    // Store pending update
    pendingUpdateRef.current = args;

    console.log('[GraphUpdate] Update requested:', {
      timeSinceLastUpdate,
      hasPendingUpdate: Boolean(updateTimeoutRef.current),
      updateType: args[0]?.type || 'unknown'
    });

    // Clear any pending update
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // Schedule update
    updateTimeoutRef.current = setTimeout(() => {
      if (updateFn && pendingUpdateRef.current) {
        console.log('[GraphUpdate] Applying update:', {
          type: pendingUpdateRef.current[0]?.type || 'unknown',
          timestamp: Date.now()
        });
        updateFn(...pendingUpdateRef.current);
        lastUpdateRef.current = Date.now();
        pendingUpdateRef.current = null;
      }
    }, Math.max(0, UPDATE_THROTTLE - timeSinceLastUpdate));
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
