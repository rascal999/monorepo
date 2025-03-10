/**
 * Application configuration
 */
export const defaultConfig = {
  // WhatsApp API configuration
  whatsapp: {
    baseUrl: "http://localhost:3000",
    apiKey: "",
    sessionId: "ABCD"
  },
  
  // Ollama API configuration
  ollama: {
    url: "http://localhost:11434",
    model: "llama2"
  },
  
  // UI configuration
  ui: {
    theme: "dark",
    messageDisplayCount: 50,
    showAnalysisPanel: true,
    showTimestamps: true,
    showReadReceipts: true
  },
  
  // Cache configuration
  cache: {
    enabled: true,
    messageMaxAge: 3600000, // 1 hour in milliseconds
    contactMaxAge: 86400000, // 24 hours
    analysisMaxAge: 1800000, // 30 minutes
    maxStorageSize: 50 * 1024 * 1024, // 50MB max cache size
    prefetchEnabled: true
  }
};

/**
 * Get the current configuration, merging default with stored user preferences
 */
export const getConfig = () => {
  try {
    const storedConfig = localStorage.getItem('whatsapp-gui-config');
    if (storedConfig) {
      return { ...defaultConfig, ...JSON.parse(storedConfig) };
    }
  } catch (error) {
    console.error('Error loading configuration:', error);
  }
  return defaultConfig;
};

/**
 * Save configuration to local storage
 */
export const saveConfig = (config) => {
  try {
    localStorage.setItem('whatsapp-gui-config', JSON.stringify(config));
    return true;
  } catch (error) {
    console.error('Error saving configuration:', error);
    return false;
  }
};

/**
 * Reset configuration to defaults
 */
export const resetConfig = () => {
  try {
    localStorage.removeItem('whatsapp-gui-config');
    return true;
  } catch (error) {
    console.error('Error resetting configuration:', error);
    return false;
  }
};

// Export current configuration
export const config = getConfig();