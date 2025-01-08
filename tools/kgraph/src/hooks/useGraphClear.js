export function useGraphClear(setGraphs, setActiveGraph, clearPersistentData) {
  const clearData = () => {
    // Clear all viewport data
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('kgraph-viewport-')) {
        localStorage.removeItem(key);
      }
    });

    // Reset state
    clearPersistentData();
    setGraphs([]);
    setActiveGraph(null);

    // Reset global callback
    if (typeof window !== 'undefined') {
      window.handleGetDefinition = null;
    }

    return null;
  };

  return clearData;
}
