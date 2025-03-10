import React from 'react';
import styled from 'styled-components';
import Message from './Message';
import { format, isToday, isYesterday, isSameDay } from 'date-fns';

/**
 * List of messages in a conversation
 */
const MessageList = ({ messages, isLoading, messagesEndRef, onScroll }) => {
  // Group messages by date
  const groupMessagesByDate = (msgs) => {
    const groups = [];
    let currentGroup = null;
    
    msgs.forEach(message => {
      const messageDate = new Date(message.timestamp);
      
      // Start a new group if this is the first message or if the date is different
      if (!currentGroup || !isSameDay(messageDate, currentGroup.date)) {
        if (currentGroup) {
          groups.push(currentGroup);
        }
        
        currentGroup = {
          date: messageDate,
          messages: [message]
        };
      } else {
        // Add to current group
        currentGroup.messages.push(message);
      }
    });
    
    // Add the last group
    if (currentGroup) {
      groups.push(currentGroup);
    }
    
    return groups;
  };
  
  // Format date for the date separator
  const formatDate = (date) => {
    if (isToday(date)) {
      return 'Today';
    } else if (isYesterday(date)) {
      return 'Yesterday';
    } else {
      return format(date, 'MMMM d, yyyy');
    }
  };
  
  // Group messages
  const messageGroups = groupMessagesByDate(messages);
  
  // Render loading state
  if (isLoading) {
    return (
      <LoadingContainer>
        <LoadingSpinner />
        <LoadingText>Loading messages...</LoadingText>
      </LoadingContainer>
    );
  }
  
  // Render empty state
  if (messages.length === 0) {
    return (
      <EmptyContainer>
        <EmptyMessage>No messages yet. Start the conversation!</EmptyMessage>
      </EmptyContainer>
    );
  }
  
  return (
    <MessageListContainer onScroll={onScroll}>
      <MessagesWrapper>
        {messageGroups.map((group, groupIndex) => (
          <MessageGroup key={groupIndex}>
            <DateSeparator>
              <DateLabel>{formatDate(group.date)}</DateLabel>
            </DateSeparator>
            
            {group.messages.map((message, messageIndex) => {
              // Ensure we have a valid key by using the message ID if available, or a fallback
              const messageKey = message.id ?
                (typeof message.id === 'object' ?
                  (message.id._serialized || `msg-${groupIndex}-${messageIndex}`) :
                  String(message.id)
                ) :
                `msg-${groupIndex}-${messageIndex}`;
              
              return (
                <Message
                  key={messageKey}
                  message={message}
                  showAvatar={
                    messageIndex === 0 ||
                    group.messages[messageIndex - 1].fromMe !== message.fromMe
                  }
                />
              );
            })}
          </MessageGroup>
        ))}
        
        {/* Invisible element for scrolling to bottom */}
        <div ref={messagesEndRef} />
      </MessagesWrapper>
    </MessageListContainer>
  );
};

// Styled components
const MessageListContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
  background-color: var(--color-background);
  
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

const MessagesWrapper = styled.div`
  display: flex;
  flex-direction: column-reverse; /* Show newest messages at the bottom */
  min-height: 100%;
`;

const MessageGroup = styled.div`
  display: flex;
  flex-direction: column-reverse;
  margin-bottom: var(--spacing-md);
`;

const DateSeparator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  margin: var(--spacing-md) 0;
`;

const DateLabel = styled.span`
  background-color: var(--color-surface-variant);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--border-radius-lg);
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--spacing-lg);
`;

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-surface-variant);
  border-top: 4px solid var(--color-primary);
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
  font-size: var(--font-size-md);
`;

const EmptyContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--spacing-lg);
`;

const EmptyMessage = styled.p`
  color: var(--color-text-secondary);
  font-size: var(--font-size-md);
  text-align: center;
`;

export default MessageList;