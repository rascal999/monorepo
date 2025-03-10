import React, { createContext, useState, useContext, useEffect } from 'react';
import { config } from '../config';

// Create the app context
const AppContext = createContext();

// Custom hook to use the app context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

// App provider component
export const AppProvider = ({ children }) => {
  // State for active chat
  const [activeChat, setActiveChat] = useState(null);
  
  // State for contacts and chats
  const [contacts, setContacts] = useState([]);
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  
  // Loading states
  const [isLoading, setIsLoading] = useState({
    contacts: false,
    chats: false,
    messages: false,
    sending: false
  });
  
  // Error states
  const [errors, setErrors] = useState({
    contacts: null,
    chats: null,
    messages: null,
    sending: null
  });
  
  // Analysis state
  const [analysisResults, setAnalysisResults] = useState({
    sentiment: null,
    relationship: null,
    suggestedResponses: []
  });
  
  // UI state
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(
    config.ui.showAnalysisPanel
  );
  
  // Session state
  const [isSessionActive, setIsSessionActive] = useState(false);
  
  // Set loading state for a specific resource
  const setLoadingState = (resource, isLoading) => {
    setIsLoading(prev => ({
      ...prev,
      [resource]: isLoading
    }));
  };
  
  // Set error state for a specific resource
  const setErrorState = (resource, error) => {
    setErrors(prev => ({
      ...prev,
      [resource]: error
    }));
  };
  
  // Clear all errors
  const clearErrors = () => {
    setErrors({
      contacts: null,
      chats: null,
      messages: null,
      sending: null
    });
  };
  
  // Toggle analysis panel
  const toggleAnalysisPanel = () => {
    setShowAnalysisPanel(prev => !prev);
  };
  
  // Context value
  const value = {
    // Chat and message state
    activeChat,
    setActiveChat,
    contacts,
    setContacts,
    chats,
    setChats,
    messages,
    setMessages,
    
    // Loading and error states
    isLoading,
    setLoadingState,
    errors,
    setErrorState,
    clearErrors,
    
    // Analysis state
    analysisResults,
    setAnalysisResults,
    showAnalysisPanel,
    toggleAnalysisPanel,
    
    // Session state
    isSessionActive,
    setIsSessionActive
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};