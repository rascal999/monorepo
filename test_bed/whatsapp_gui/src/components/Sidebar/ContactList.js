import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';

/**
 * List of contacts
 */
const ContactList = ({ searchQuery }) => {
  const { 
    contacts, 
    setActiveChat, 
    isLoading, 
    setLoadingState,
    setErrorState
  } = useApp();
  
  // Filter contacts based on search query
  const filteredContacts = searchQuery 
    ? contacts.filter(contact => 
        contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.number.includes(searchQuery)
      )
    : contacts;
  
  // Sort contacts alphabetically by name
  const sortedContacts = [...filteredContacts].sort((a, b) => 
    a.name.localeCompare(b.name)
  );
  
  // Start a new chat with a contact
  const startChat = async (contact) => {
    try {
      setLoadingState('chats', true);
      
      // Find or create chat for this contact
      const response = await api.findContact(contact.number);
      
      if (response && response.chat) {
        setActiveChat(response.chat);
      } else {
        // Handle case where chat doesn't exist yet
        console.log('No existing chat found for contact');
        // You might want to create a new chat here
      }
      
      setLoadingState('chats', false);
    } catch (error) {
      console.error('Error starting chat:', error);
      setErrorState('chats', error.message);
      setLoadingState('chats', false);
    }
  };
  
  // Get the avatar initials
  const getInitials = (name) => {
    if (!name) return '?';
    
    const parts = name.split(' ');
    if (parts.length === 1) {
      return parts[0].charAt(0).toUpperCase();
    }
    
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  };
  
  // Render loading state
  if (isLoading.contacts) {
    return (
      <LoadingContainer>
        <LoadingSpinner />
        <LoadingText>Loading contacts...</LoadingText>
      </LoadingContainer>
    );
  }
  
  // Render empty state
  if (sortedContacts.length === 0) {
    return (
      <EmptyContainer>
        {searchQuery ? (
          <EmptyMessage>No contacts match your search.</EmptyMessage>
        ) : (
          <EmptyMessage>No contacts available.</EmptyMessage>
        )}
      </EmptyContainer>
    );
  }
  
  return (
    <ContactListContainer>
      {sortedContacts.map(contact => (
        <ContactItem key={contact.id} onClick={() => startChat(contact)}>
          <Avatar>
            {getInitials(contact.name)}
          </Avatar>
          
          <ContactInfo>
            <ContactName>{contact.name}</ContactName>
            <ContactNumber>{contact.number}</ContactNumber>
          </ContactInfo>
          
          <ChatButton>
            <ChatIcon>💬</ChatIcon>
          </ChatButton>
        </ContactItem>
      ))}
    </ContactListContainer>
  );
};

// Styled components
const ContactListContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const ContactItem = styled.div`
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-divider);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: var(--color-surface-variant);
  }
`;

const Avatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--color-secondary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  font-weight: bold;
  margin-right: var(--spacing-md);
  flex-shrink: 0;
`;

const ContactInfo = styled.div`
  flex: 1;
  min-width: 0; /* Enables text truncation */
`;

const ContactName = styled.h3`
  font-size: var(--font-size-md);
  font-weight: bold;
  margin: 0;
  margin-bottom: var(--spacing-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ContactNumber = styled.p`
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ChatButton = styled.button`
  background: none;
  border: none;
  color: var(--color-primary);
  padding: var(--spacing-sm);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: rgba(0, 168, 132, 0.1);
  }
`;

const ChatIcon = styled.span`
  font-size: var(--font-size-lg);
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  padding: var(--spacing-lg);
`;

const LoadingSpinner = styled.div`
  width: 30px;
  height: 30px;
  border: 3px solid var(--color-surface-variant);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.p`
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
`;

const EmptyContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  padding: var(--spacing-lg);
`;

const EmptyMessage = styled.p`
  color: var(--color-text-secondary);
  font-size: var(--font-size-md);
  text-align: center;
`;

export default ContactList;