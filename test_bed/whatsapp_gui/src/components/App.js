import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useApp } from '../context/AppContext';
import { useTheme } from '../context/ThemeContext';
import Sidebar from './Sidebar/Sidebar';
import ChatView from './ChatView/ChatView';
import AnalysisPanel from './Analysis/AnalysisPanel';
import api from '../services/api';

/**
 * Main application component
 */
const App = () => {
  const { 
    activeChat, 
    setContacts, 
    setChats, 
    setLoadingState, 
    setErrorState,
    isSessionActive,
    setIsSessionActive,
    showAnalysisPanel
  } = useApp();
  
  const { isDarkMode } = useTheme();
  const [isInitializing, setIsInitializing] = useState(true);
  
  // Initialize the application
  useEffect(() => {
    const initialize = async () => {
      try {
        // Check if session exists
        const sessionExists = await api.checkSession();
        
        if (!sessionExists) {
          // Start a new session if one doesn't exist
          await api.startSession();
          
          // Wait for connection
          const connected = await api.waitForConnection();
          if (!connected) {
            throw new Error('Failed to connect to WhatsApp');
          }
        }
        
        setIsSessionActive(true);
        
        // Load initial data
        await loadInitialData();
        
        setIsInitializing(false);
      } catch (error) {
        console.error('Error initializing app:', error);
        setErrorState('app', error.message);
        setIsInitializing(false);
      }
    };
    
    initialize();
  }, []);
  
  // Load contacts and chats
  const loadInitialData = async () => {
    try {
      // Load contacts
      setLoadingState('contacts', true);
      const contacts = await api.getContacts();
      setContacts(contacts);
      setLoadingState('contacts', false);
      
      // Load chats
      setLoadingState('chats', true);
      const chats = await api.getChats();
      setChats(chats);
      setLoadingState('chats', false);
    } catch (error) {
      console.error('Error loading initial data:', error);
      setErrorState('app', error.message);
    }
  };
  
  // Render loading state
  if (isInitializing) {
    return (
      <LoadingContainer>
        <LoadingSpinner />
        <LoadingText>Connecting to WhatsApp...</LoadingText>
      </LoadingContainer>
    );
  }
  
  // Render error state if session failed
  if (!isSessionActive) {
    return (
      <ErrorContainer>
        <ErrorIcon>⚠️</ErrorIcon>
        <ErrorTitle>Connection Error</ErrorTitle>
        <ErrorMessage>
          Failed to connect to WhatsApp. Please check your configuration and try again.
        </ErrorMessage>
        <RetryButton onClick={() => window.location.reload()}>
          Retry
        </RetryButton>
      </ErrorContainer>
    );
  }
  
  return (
    <AppContainer isDarkMode={isDarkMode}>
      <Sidebar />
      
      <MainContent>
        {activeChat ? (
          <>
            <ChatView />
            {showAnalysisPanel && <AnalysisPanel />}
          </>
        ) : (
          <WelcomeScreen>
            <WelcomeTitle>Welcome to WhatsApp GUI</WelcomeTitle>
            <WelcomeMessage>
              Select a chat from the sidebar to get started.
            </WelcomeMessage>
          </WelcomeScreen>
        )}
      </MainContent>
    </AppContainer>
  );
};

// Styled components
const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  width: 100%;
  background-color: var(--color-background);
  color: var(--color-text-primary);
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  height: 100%;
  overflow: hidden;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100%;
  background-color: var(--color-background);
  color: var(--color-text-primary);
`;

const LoadingSpinner = styled.div`
  width: 50px;
  height: 50px;
  border: 5px solid var(--color-surface-variant);
  border-top: 5px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.p`
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
`;

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100%;
  background-color: var(--color-background);
  color: var(--color-text-primary);
  padding: var(--spacing-xl);
  text-align: center;
`;

const ErrorIcon = styled.div`
  font-size: 48px;
  margin-bottom: var(--spacing-lg);
`;

const ErrorTitle = styled.h2`
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-md);
  color: var(--color-error);
`;

const ErrorMessage = styled.p`
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
  max-width: 500px;
`;

const RetryButton = styled.button`
  background-color: var(--color-primary);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: var(--color-primary-variant);
  }
`;

const WelcomeScreen = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  background-color: var(--color-surface);
  padding: var(--spacing-xl);
  text-align: center;
`;

const WelcomeTitle = styled.h1`
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-lg);
  color: var(--color-primary);
`;

const WelcomeMessage = styled.p`
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  max-width: 500px;
`;

export default App;