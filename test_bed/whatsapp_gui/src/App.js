import React from 'react';
import styled from 'styled-components';
import { AppProvider, AppContext } from './context/AppContext';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar/Sidebar';
import ChatView from './components/ChatView/ChatView';
import AnalysisPanel from './components/Analysis/AnalysisPanel';
import './styles/global.css';

/**
 * Main App component
 */
const App = () => {
  return (
    <ThemeProvider>
      <AppProvider>
        <AppContainer>
          <Sidebar />
          <MainContent />
        </AppContainer>
      </AppProvider>
    </ThemeProvider>
  );
};

/**
 * Main content component that conditionally renders the chat view and analysis panel
 */
const MainContent = () => {
  const { activeChat, showAnalysisPanel } = React.useContext(AppContext);
  
  if (!activeChat) {
    return (
      <EmptyStateContainer>
        <EmptyStateContent>
          <EmptyStateIcon>💬</EmptyStateIcon>
          <EmptyStateTitle>WhatsApp GUI</EmptyStateTitle>
          <EmptyStateDescription>
            Select a chat to start messaging or use the search to find contacts.
          </EmptyStateDescription>
        </EmptyStateContent>
      </EmptyStateContainer>
    );
  }
  
  return (
    <ContentContainer>
      <ChatView />
      {showAnalysisPanel && <AnalysisPanel />}
    </ContentContainer>
  );
};

// Styled components
const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text-primary);
`;

const ContentContainer = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const EmptyStateContainer = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface);
`;

const EmptyStateContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 400px;
  padding: var(--spacing-lg);
`;

const EmptyStateIcon = styled.div`
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
`;

const EmptyStateTitle = styled.h1`
  font-size: var(--font-size-xl);
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-primary);
`;

const EmptyStateDescription = styled.p`
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
`;

export default App;