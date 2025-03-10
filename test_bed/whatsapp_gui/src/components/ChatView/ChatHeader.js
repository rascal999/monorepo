import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';

/**
 * Header for the chat view showing contact info
 */
const ChatHeader = ({ chat }) => {
  const { toggleAnalysisPanel, showAnalysisPanel } = useApp();
  
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
    <HeaderContainer>
      <ContactInfo>
        <Avatar>
          {getInitials(chat.name)}
        </Avatar>
        
        <ContactDetails>
          <ContactName>{chat.name}</ContactName>
          {chat.isOnline && <OnlineStatus>Online</OnlineStatus>}
        </ContactDetails>
      </ContactInfo>
      
      <HeaderActions>
        <ActionButton 
          title={showAnalysisPanel ? "Hide analysis" : "Show analysis"}
          onClick={toggleAnalysisPanel}
          active={showAnalysisPanel}
        >
          <span>🧠</span>
        </ActionButton>
        
        <ActionButton title="Search in conversation">
          <span>🔍</span>
        </ActionButton>
        
        <ActionButton title="More options">
          <span>⋮</span>
        </ActionButton>
      </HeaderActions>
    </HeaderContainer>
  );
};

// Styled components
const HeaderContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--color-surface-variant);
  border-bottom: 1px solid var(--color-divider);
  height: 60px;
`;

const ContactInfo = styled.div`
  display: flex;
  align-items: center;
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary-variant);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-md);
  font-weight: bold;
  margin-right: var(--spacing-md);
`;

const ContactDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const ContactName = styled.h2`
  font-size: var(--font-size-md);
  font-weight: bold;
  margin: 0;
  margin-bottom: var(--spacing-xs);
`;

const OnlineStatus = styled.span`
  font-size: var(--font-size-xs);
  color: var(--color-success);
`;

const HeaderActions = styled.div`
  display: flex;
  gap: var(--spacing-sm);
`;

const ActionButton = styled.button`
  background: ${props => props.active ? 'var(--color-primary-variant)' : 'none'};
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color var(--transition-fast);
  
  span {
    font-size: var(--font-size-md);
  }
  
  &:hover {
    background-color: ${props => 
      props.active ? 'var(--color-primary)' : 'var(--color-surface-hover)'};
  }
`;

export default ChatHeader;