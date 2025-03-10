import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';
import ChatItem from './ChatItem';

/**
 * List of chats in the sidebar
 */
const ChatList = ({ searchQuery }) => {
  const { 
    chats, 
    activeChat, 
    setActiveChat, 
    isLoading, 
    setLoadingState,
    setErrorState
  } = useApp();
  
  // Filter chats based on search query
  const filteredChats = searchQuery 
    ? chats.filter(chat => 
        chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (chat.lastMessage && chat.lastMessage.body.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : chats;
  
  // Sort chats by last message timestamp (most recent first)
  const sortedChats = [...filteredChats].sort((a, b) => {
    const timeA = a.lastMessage ? new Date(a.lastMessage.timestamp).getTime() : 0;
    const timeB = b.lastMessage ? new Date(b.lastMessage.timestamp).getTime() : 0;
    return timeB - timeA;
  });
  
  // Handle chat selection
  const handleChatSelect = async (chat) => {
    try {
      setLoadingState('messages', true);
      setActiveChat(chat);
      setLoadingState('messages', false);
    } catch (error) {
      console.error('Error selecting chat:', error);
      setErrorState('messages', error.message);
      setLoadingState('messages', false);
    }
  };
  
  // Render loading state
  if (isLoading.chats) {
    return (
      <LoadingContainer>
        <LoadingSpinner />
        <LoadingText>Loading chats...</LoadingText>
      </LoadingContainer>
    );
  }
  
  // Render empty state
  if (sortedChats.length === 0) {
    return (
      <EmptyContainer>
        {searchQuery ? (
          <EmptyMessage>No chats match your search.</EmptyMessage>
        ) : (
          <EmptyMessage>No chats available. Start a new conversation from the Contacts tab.</EmptyMessage>
        )}
      </EmptyContainer>
    );
  }
  
  return (
    <ChatListContainer>
      {sortedChats.map((chat, index) => {
        // Ensure we have a valid key by using the chat ID if available, or a fallback
        const chatKey = chat.id ?
          (typeof chat.id === 'object' ?
            (chat.id._serialized || `chat-${index}`) :
            String(chat.id)
          ) :
          `chat-${index}`;
        
        // Check if this chat is active, handling object IDs
        const isActive = activeChat && (
          activeChat.id === chat.id ||
          (typeof activeChat.id === 'object' &&
           typeof chat.id === 'object' &&
           activeChat.id._serialized === chat.id._serialized)
        );
        
        return (
          <ChatItem
            key={chatKey}
            chat={chat}
            isActive={isActive}
            onClick={() => handleChatSelect(chat)}
          />
        );
      })}
    </ChatListContainer>
  );
};

// Styled components
const ChatListContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: var(--color-divider);
    border-radius: 3px;
  }
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

export default ChatList;