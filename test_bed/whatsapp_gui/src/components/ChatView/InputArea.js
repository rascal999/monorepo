import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

/**
 * Input area for typing and sending messages
 */
const InputArea = ({ onSendMessage, isTyping, disabled }) => {
  const [message, setMessage] = useState('');
  const [isEmojiPickerOpen, setIsEmojiPickerOpen] = useState(false);
  const textareaRef = useRef(null);
  
  // Focus textarea on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);
  
  // Auto-resize textarea as user types
  useEffect(() => {
    if (textareaRef.current) {
      // Reset height to auto to get the correct scrollHeight
      textareaRef.current.style.height = 'auto';
      
      // Set new height based on scrollHeight (with max height)
      const newHeight = Math.min(textareaRef.current.scrollHeight, 120);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, [message]);
  
  // Handle message input change
  const handleChange = (e) => {
    setMessage(e.target.value);
  };
  
  // Handle key press (Enter to send, Shift+Enter for new line)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  // Send message
  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };
  
  // Toggle emoji picker
  const toggleEmojiPicker = () => {
    setIsEmojiPickerOpen(!isEmojiPickerOpen);
  };
  
  // Add emoji to message
  const addEmoji = (emoji) => {
    setMessage(prev => prev + emoji);
    textareaRef.current.focus();
  };
  
  return (
    <InputContainer>
      {/* Emoji picker would be implemented here */}
      {isEmojiPickerOpen && (
        <EmojiPickerContainer>
          <EmojiGrid>
            {['😊', '😂', '❤️', '👍', '🙏', '😍', '😭', '🔥', '🎉', '🤔', '😎', '👏', '🥰', '😢', '😡', '🤣', '😴', '🤮', '🤑', '🤯'].map(emoji => (
              <EmojiButton 
                key={emoji} 
                onClick={() => addEmoji(emoji)}
              >
                {emoji}
              </EmojiButton>
            ))}
          </EmojiGrid>
        </EmojiPickerContainer>
      )}
      
      <InputControls>
        <ControlButton onClick={toggleEmojiPicker} active={isEmojiPickerOpen}>
          <span>😊</span>
        </ControlButton>
        
        <ControlButton>
          <span>📎</span>
        </ControlButton>
      </InputControls>
      
      <MessageInput
        ref={textareaRef}
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Type a message"
        disabled={disabled}
        rows={1}
      />
      
      <SendButton 
        onClick={handleSend} 
        disabled={!message.trim() || disabled}
      >
        {isTyping ? (
          <LoadingDots>
            <span>.</span><span>.</span><span>.</span>
          </LoadingDots>
        ) : (
          <span>➤</span>
        )}
      </SendButton>
    </InputContainer>
  );
};

// Styled components
const InputContainer = styled.div`
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-md);
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-divider);
  position: relative;
`;

const InputControls = styled.div`
  display: flex;
  align-items: center;
  margin-right: var(--spacing-sm);
`;

const ControlButton = styled.button`
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color var(--transition-fast);
  color: var(--color-text-secondary);
  background-color: ${props => props.active ? 'var(--color-surface-variant)' : 'transparent'};
  
  span {
    font-size: var(--font-size-md);
  }
  
  &:hover {
    background-color: var(--color-surface-variant);
  }
`;

const MessageInput = styled.textarea`
  flex: 1;
  background-color: var(--color-surface-variant);
  border: none;
  border-radius: var(--border-radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
  resize: none;
  min-height: 40px;
  max-height: 120px;
  
  &:focus {
    outline: none;
  }
  
  &::placeholder {
    color: var(--color-text-muted);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const SendButton = styled.button`
  background-color: ${props => 
    props.disabled ? 'var(--color-surface-variant)' : 'var(--color-primary)'};
  color: ${props => 
    props.disabled ? 'var(--color-text-muted)' : 'white'};
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  margin-left: var(--spacing-sm);
  transition: background-color var(--transition-fast);
  
  span {
    font-size: var(--font-size-md);
  }
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-variant);
  }
`;

const EmojiPickerContainer = styled.div`
  position: absolute;
  bottom: 70px;
  left: var(--spacing-md);
  background-color: var(--color-surface);
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: var(--spacing-md);
  z-index: 10;
  width: 300px;
`;

const EmojiGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--spacing-sm);
`;

const EmojiButton = styled.button`
  background: none;
  border: none;
  font-size: var(--font-size-lg);
  padding: var(--spacing-sm);
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: var(--color-surface-variant);
  }
`;

const LoadingDots = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  
  span {
    animation: loadingDots 1.4s infinite both;
    font-size: var(--font-size-lg);
    line-height: 0.5;
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
  
  @keyframes loadingDots {
    0% { opacity: 0.2; transform: translateY(0); }
    20% { opacity: 1; transform: translateY(-3px); }
    40% { opacity: 0.2; transform: translateY(0); }
  }
`;

export default InputArea;