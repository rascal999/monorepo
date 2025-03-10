import React from 'react';
import styled from 'styled-components';
import { format } from 'date-fns';
import { useTheme } from '../../context/ThemeContext';
import { config } from '../../config';

/**
 * Individual message component
 */
const Message = ({ message, showAvatar }) => {
  const { isDarkMode } = useTheme();
  
  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    return format(new Date(timestamp), 'HH:mm');
  };
  
  // Get message status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'sending':
        return '🕒'; // Clock
      case 'sent':
        return '✓'; // Single check
      case 'delivered':
        return '✓✓'; // Double check
      case 'read':
        return '✓✓'; // Double check (blue in the styled component)
      case 'failed':
        return '⚠️'; // Warning
      default:
        return '';
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
  
  return (
    <MessageContainer fromMe={message.fromMe}>
      {!message.fromMe && showAvatar && (
        <Avatar>
          {getInitials(message.senderName || 'Them')}
        </Avatar>
      )}
      
      {!message.fromMe && !showAvatar && <AvatarSpacer />}
      
      <MessageContent fromMe={message.fromMe} isDarkMode={isDarkMode}>
        {!message.fromMe && message.senderName && showAvatar && (
          <SenderName>{message.senderName}</SenderName>
        )}
        
        <MessageText>{message.body}</MessageText>
        
        <MessageMeta>
          <MessageTime>{formatTime(message.timestamp)}</MessageTime>
          
          {message.fromMe && config.ui.showReadReceipts && (
            <MessageStatus status={message.status}>
              {getStatusIcon(message.status)}
            </MessageStatus>
          )}
        </MessageMeta>
      </MessageContent>
    </MessageContainer>
  );
};

// Styled components
const MessageContainer = styled.div`
  display: flex;
  flex-direction: ${props => props.fromMe ? 'row-reverse' : 'row'};
  align-items: flex-end;
  margin-bottom: var(--spacing-sm);
  max-width: 85%;
  align-self: ${props => props.fromMe ? 'flex-end' : 'flex-start'};
`;

const Avatar = styled.div`
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: var(--color-secondary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: bold;
  margin-right: var(--spacing-sm);
  flex-shrink: 0;
`;

const AvatarSpacer = styled.div`
  width: 30px;
  margin-right: var(--spacing-sm);
`;

const MessageContent = styled.div`
  background-color: ${props => 
    props.fromMe 
      ? 'var(--color-primary-light)' 
      : 'var(--color-surface-variant)'};
  color: var(--color-text-primary);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  position: relative;
  max-width: 100%;
  
  /* Message tail */
  &:before {
    content: '';
    position: absolute;
    bottom: 8px;
    width: 8px;
    height: 13px;
    ${props => props.fromMe 
      ? 'right: -8px; background: radial-gradient(circle at top right, transparent 70%, var(--color-primary-light) 0);' 
      : 'left: -8px; background: radial-gradient(circle at top left, transparent 70%, var(--color-surface-variant) 0);'
    }
  }
`;

const SenderName = styled.div`
  font-size: var(--font-size-xs);
  font-weight: bold;
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
`;

const MessageText = styled.p`
  margin: 0;
  font-size: var(--font-size-md);
  white-space: pre-wrap;
  word-break: break-word;
`;

const MessageMeta = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: var(--spacing-xs);
  gap: var(--spacing-xs);
`;

const MessageTime = styled.span`
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
`;

const MessageStatus = styled.span`
  font-size: var(--font-size-xs);
  color: ${props => {
    if (props.status === 'read') {
      return 'var(--color-primary)';
    } else if (props.status === 'failed') {
      return 'var(--color-error)';
    } else {
      return 'var(--color-text-secondary)';
    }
  }};
`;

export default Message;