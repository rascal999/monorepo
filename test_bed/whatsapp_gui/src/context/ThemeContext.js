import React, { createContext, useState, useContext, useEffect } from 'react';
import { config, saveConfig } from '../config';

// Create the theme context
const ThemeContext = createContext();

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme provider component
export const ThemeProvider = ({ children }) => {
  // Initialize theme from config
  const [theme, setTheme] = useState(config.ui.theme || 'dark');
  
  // Apply theme to document when it changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update config when theme changes
    const updatedConfig = {
      ...config,
      ui: {
        ...config.ui,
        theme
      }
    };
    saveConfig(updatedConfig);
  }, [theme]);
  
  // Toggle between light and dark themes
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };
  
  // Set a specific theme
  const setThemeMode = (mode) => {
    if (mode === 'dark' || mode === 'light') {
      setTheme(mode);
    }
  };
  
  // Context value
  const value = {
    theme,
    isDarkMode: theme === 'dark',
    toggleTheme,
    setTheme: setThemeMode
  };
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};