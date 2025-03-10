import React, { useState } from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';
import { useTheme } from '../../context/ThemeContext';
import SearchBar from './SearchBar';
import ChatList from './ChatList';
import ContactList from './ContactList';

/**
 * Sidebar component containing search, chats, and contacts
 */
const Sidebar = () => {
  const { toggleTheme } = useTheme();
  const { 
    isLoading, 
    refreshChats, 
    refreshContacts 
  } = useApp();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('chats');
  
  // Handle search input
  const handleSearch = (query) => {
    setSearchQuery(query);
  };
  
  // Switch between tabs
  const switchTab = (tab) => {
    setActiveTab(tab);
  };
  
  // Refresh data
  const handleRefresh = () => {
    if (activeTab === 'chats') {
      refreshChats();
    } else {
      refreshContacts();
    }
  };
  
  return (
    <SidebarContainer>
      <SidebarHeader>
        <HeaderTitle>WhatsApp GUI</HeaderTitle>
        
        <HeaderActions>
          <ActionButton onClick={toggleTheme} title="Toggle theme">
            <span>🌓</span>
          </ActionButton>
          
          <ActionButton onClick={handleRefresh} disabled={isLoading[activeTab]} title="Refresh">
            <span>🔄</span>
          </ActionButton>
          
          <ActionButton title="Settings">
            <span>⚙️</span>
          </ActionButton>
        </HeaderActions>
      </SidebarHeader>
      
      <SearchBar onSearch={handleSearch} />
      
      <TabsContainer>
        <Tab 
          active={activeTab === 'chats'} 
          onClick={() => switchTab('chats')}
        >
          Chats
        </Tab>
        <Tab 
          active={activeTab === 'contacts'} 
          onClick={() => switchTab('contacts')}
        >
          Contacts
        </Tab>
      </TabsContainer>
      
      {activeTab === 'chats' ? (
        <ChatList searchQuery={searchQuery} />
      ) : (
        <ContactList searchQuery={searchQuery} />
      )}
    </SidebarContainer>
  );
};

// Styled components
const SidebarContainer = styled.div`
  width: 350px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-divider);
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--color-surface-variant);
  height: 60px;
`;

const HeaderTitle = styled.h1`
  font-size: var(--font-size-lg);
  margin: 0;
  color: var(--color-primary);
`;

const HeaderActions = styled.div`
  display: flex;
  gap: var(--spacing-sm);
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.5 : 1};
  transition: background-color var(--transition-fast);
  
  span {
    font-size: var(--font-size-md);
  }
  
  &:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid var(--color-divider);
`;

const Tab = styled.button`
  flex: 1;
  padding: var(--spacing-md);
  background: none;
  border: none;
  border-bottom: 2px solid ${props => 
    props.active ? 'var(--color-primary)' : 'transparent'};
  color: ${props => 
    props.active ? 'var(--color-primary)' : 'var(--color-text-secondary)'};
  font-weight: ${props => props.active ? 'bold' : 'normal'};
  font-size: var(--font-size-md);
  transition: all var(--transition-fast);
  
  &:hover {
    background-color: var(--color-surface-variant);
  }
`;

export default Sidebar;