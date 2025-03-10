import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';

/**
 * Component for displaying suggested responses
 */
const SuggestedResponses = ({ responses }) => {
  const { activeChat, setMessages } = useApp();
  
  // If no responses are available yet
  if (!responses || responses.length === 0) {
    return (
      <EmptyContainer>
        <EmptyMessage>
          No suggested responses available. Send more messages to generate suggestions.
        </EmptyMessage>
      </EmptyContainer>
    );
  }
  
  // Get tone color
  const getToneColor = (tone) => {
    switch (tone.toLowerCase()) {
      case 'positive':
      case 'friendly':
      case 'enthusiastic':
        return 'var(--color-success)';
      case 'negative':
      case 'angry':
        return 'var(--color-error)';
      case 'neutral':
        return 'var(--color-text-secondary)';
      case 'formal':
        return 'var(--color-primary)';
      case 'casual':
        return 'var(--color-secondary)';
      case 'empathetic':
        return 'var(--color-tertiary)';
      default:
        return 'var(--color-text-secondary)';
    }
  };
  
  // Get purpose icon
  const getPurposeIcon = (purpose) => {
    switch (purpose.toLowerCase()) {
      case 'question':
        return '❓';
      case 'answer':
        return '💡';
      case 'greeting':
        return '👋';
      case 'farewell':
        return '👋';
      case 'acknowledgment':
        return '👍';
      case 'clarification':
        return '🔍';
      case 'agreement':
        return '✅';
      case 'disagreement':
        return '❌';
      case 'suggestion':
        return '💭';
      case 'request':
        return '🙏';
      default:
        return '💬';
    }
  };
  
  // Send a suggested response
  const sendResponse = (text) => {
    if (!activeChat) return;
    
    // Add message to input (in a real app, this would send the message)
    // For demo purposes, we'll just add it to the messages list
    const newMessage = {
      id: `suggested-${Date.now()}`,
      body: text,
      fromMe: true,
      timestamp: new Date().toISOString(),
      status: 'sent'
    };
    
    setMessages(prev => [newMessage, ...prev]);
  };
  
  return (
    <ResponsesContainer>
      <ResponsesHeader>
        <ResponsesTitle>Suggested Responses</ResponsesTitle>
        <ResponsesSubtitle>
          Click on a response to use it
        </ResponsesSubtitle>
      </ResponsesHeader>
      
      <ResponsesList>
        {responses.map((response, index) => (
          <ResponseItem
            key={index}
            onClick={() => sendResponse(response.text)}
          >
            <ResponseText>{response.text}</ResponseText>
            
            <ResponseMeta>
              {response.tone && (
                <ResponseTone color={getToneColor(response.tone)}>
                  {response.tone}
                </ResponseTone>
              )}
              
              {response.purpose && (
                <ResponsePurpose>
                  {getPurposeIcon(response.purpose)} {response.purpose}
                </ResponsePurpose>
              )}
            </ResponseMeta>
          </ResponseItem>
        ))}
      </ResponsesList>
      
      <DisclaimerText>
        These responses are AI-generated suggestions based on the conversation context.
      </DisclaimerText>
    </ResponsesContainer>
  );
};

// Styled components
const ResponsesContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const ResponsesHeader = styled.div`
  margin-bottom: var(--spacing-md);
`;

const ResponsesTitle = styled.h3`
  font-size: var(--font-size-md);
  margin: 0 0 var(--spacing-xs) 0;
`;

const ResponsesSubtitle = styled.p`
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
`;

const ResponsesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
`;

const ResponseItem = styled.div`
  background-color: var(--color-surface-variant);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  transition: background-color var(--transition-fast), transform var(--transition-fast);
  
  &:hover {
    background-color: var(--color-surface-hover);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const ResponseText = styled.p`
  font-size: var(--font-size-md);
  margin: 0 0 var(--spacing-sm) 0;
  line-height: 1.5;
`;

const ResponseMeta = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
`;

const ResponseTone = styled.div`
  font-size: var(--font-size-xs);
  color: ${props => props.color};
  font-weight: bold;
`;

const ResponsePurpose = styled.div`
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
`;

const DisclaimerText = styled.p`
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-style: italic;
  margin: 0;
  text-align: center;
`;

const EmptyContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
`;

const EmptyMessage = styled.p`
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  text-align: center;
`;

export default SuggestedResponses;