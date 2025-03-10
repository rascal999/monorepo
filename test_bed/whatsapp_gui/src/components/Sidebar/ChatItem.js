import React from 'react';
import styled from 'styled-components';

/**
 * Individual chat item in the chat list
 */
const ChatItem = ({ chat, isActive, onClick }) => {
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };
  
  // Get message preview (truncate if too long)
  const getMessagePreview = (message) => {
    if (!message) return '';
    
    const MAX_LENGTH = 40;
    if (message.length <= MAX_LENGTH) return message;
    return message.substring(0, MAX_LENGTH) + '...';
  };
  
  // Get unread count display
  const getUnreadDisplay = (count) => {
    if (!count) return null;
    if (count > 99) return '99+';
    return count.toString();
  };
  
  return (
    <ChatItemContainer 
      active={isActive}
      onClick={onClick}
    >
      <Avatar>
        {chat.name ? chat.name.charAt(0).toUpperCase() : '?'}
      </Avatar>
      
      <ChatInfo>
        <ChatHeader>
          <ChatName>{chat.name}</ChatName>
          {chat.lastMessage && (
            <ChatTime>{formatTimestamp(chat.lastMessage.timestamp)}</ChatTime>
          )}
        </ChatHeader>
        
        <ChatPreview>
          {chat.lastMessage ? (
            <LastMessage>
              {chat.lastMessage.fromMe && <SentIndicator>You: </SentIndicator>}
              {getMessagePreview(chat.lastMessage.body)}
            </LastMessage>
          ) : (
            <NoMessages>No messages yet</NoMessages>
          )}
          
          {chat.unreadCount > 0 && (
            <UnreadBadge>
              {getUnreadDisplay(chat.unreadCount)}
            </UnreadBadge>
          )}
        </ChatPreview>
      </ChatInfo>
    </ChatItemContainer>
  );
};

// Styled components
const ChatItemContainer = styled.div`
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  cursor: pointer;
  background-color: ${props => 
    props.active ? 'var(--color-surface-selected)' : 'transparent'};
  border-bottom: 1px solid var(--color-divider);
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: ${props => 
      props.active ? 'var(--color-surface-selected)' : 'var(--color-surface-hover)'};
  }
`;

const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  font-weight: bold;
  margin-right: var(--spacing-md);
  flex-shrink: 0;
`;

const ChatInfo = styled.div`
  flex: 1;
  min-width: 0; /* Needed for text truncation */
  display: flex;
  flex-direction: column;
`;

const ChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
`;

const ChatName = styled.div`
  font-weight: bold;
  font-size: var(--font-size-md);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ChatTime = styled.div`
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  flex-shrink: 0;
  margin-left: var(--spacing-sm);
`;

const ChatPreview = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const LastMessage = styled.div`
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const SentIndicator = styled.span`
  color: var(--color-text-muted);
`;

const NoMessages = styled.div`
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  font-style: italic;
`;

const UnreadBadge = styled.div`
  background-color: var(--color-primary);
  color: white;
  font-size: var(--font-size-xs);
  font-weight: bold;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--spacing-xs);
  margin-left: var(--spacing-sm);
  flex-shrink: 0;
`;

export default ChatItem;