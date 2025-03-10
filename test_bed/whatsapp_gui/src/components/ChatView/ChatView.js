import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import InputArea from './InputArea';
import api from '../../services/api';
import messageCache from '../../cache/messageCache';
import { config } from '../../config';

/**
 * Main chat view component
 */
const ChatView = () => {
  const { 
    activeChat, 
    messages, 
    setMessages, 
    setLoadingState, 
    isLoading,
    setErrorState,
    setAnalysisResults
  } = useApp();
  
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Fetch messages when active chat changes
  useEffect(() => {
    if (!activeChat) return;
    
    const fetchMessages = async () => {
      try {
        setLoadingState('messages', true);
        
        // Normalize chat ID
        const chatId = typeof activeChat.id === 'object' && activeChat.id._serialized
          ? activeChat.id._serialized
          : activeChat.id;
        
        console.log('Fetching messages for chat ID:', chatId);
        
        // Use cache with fallback to API
        const fetchFromApi = (chatId, limit) => api.getMessages(chatId, limit);
        
        // Only fetch recent messages (last 20) initially
        const recentLimit = 20;
        const chatMessages = await messageCache.getMessages(
          chatId,
          recentLimit,
          0,
          fetchFromApi
        );
        
        setMessages(chatMessages);
        setLoadingState('messages', false);
      } catch (error) {
        console.error('Error fetching messages:', error);
        setErrorState('messages', error.message);
        setLoadingState('messages', false);
      }
    };
    
    fetchMessages();
  }, [activeChat, setMessages, setLoadingState, setErrorState]);
  
  // Handle scrolling to load more messages
  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    
    // If scrolled near the top, load more messages
    if (scrollTop < 50 && !isLoading.messages && messages.length >= 20) {
      loadMoreMessages();
    }
  };
  
  // Load more messages when scrolling up
  const loadMoreMessages = async () => {
    if (!activeChat || isLoading.messages) return;
    
    try {
      setLoadingState('messages', true);
      
      // Normalize chat ID
      const chatId = typeof activeChat.id === 'object' && activeChat.id._serialized
        ? activeChat.id._serialized
        : activeChat.id;
      
      console.log('Loading more messages for chat ID:', chatId);
      
      const fetchFromApi = (chatId, limit, offset) => api.getMessages(chatId, limit, offset);
      const olderMessages = await messageCache.getMessages(
        chatId,
        20, // Load 20 more messages
        messages.length, // Offset by current message count
        fetchFromApi
      );
      
      if (olderMessages.length > 0) {
        setMessages(prev => [...prev, ...olderMessages]);
      }
      
      setLoadingState('messages', false);
    } catch (error) {
      console.error('Error loading more messages:', error);
      setErrorState('messages', error.message);
      setLoadingState('messages', false);
    }
  };
  
  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Send a message
  const sendMessage = async (text) => {
    if (!text.trim() || !activeChat) return;
    
    try {
      setIsTyping(true);
      setLoadingState('sending', true);
      
      // Normalize chat ID
      const chatId = typeof activeChat.id === 'object' && activeChat.id._serialized
        ? activeChat.id._serialized
        : activeChat.id;
      
      console.log('Sending message to chat ID:', chatId);
      
      // Optimistic update
      const tempMessage = {
        id: `temp-${Date.now()}`,
        body: text,
        fromMe: true,
        timestamp: new Date().toISOString(),
        status: 'sending'
      };
      
      setMessages(prev => [tempMessage, ...prev]);
      
      // Send to API
      const response = await api.sendMessage(chatId, text);
      
      // Update with actual message
      setMessages(prev =>
        prev.map(msg =>
          msg.id === tempMessage.id ? { ...response, status: 'sent' } : msg
        )
      );
      
      // Invalidate cache
      await messageCache.invalidateCache(chatId);
      
      setLoadingState('sending', false);
      setIsTyping(false);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Update failed message status
      setMessages(prev =>
        prev.map(msg =>
          msg.id === `temp-${Date.now()}` ? { ...msg, status: 'failed' } : msg
        )
      );
      
      setErrorState('sending', error.message);
      setLoadingState('sending', false);
      setIsTyping(false);
    }
  };
  
  if (!activeChat) {
    return null;
  }
  
  return (
    <ChatViewContainer>
      <ChatHeader chat={activeChat} />
      
      <MessageList
        messages={messages}
        isLoading={isLoading.messages}
        messagesEndRef={messagesEndRef}
        onScroll={handleScroll}
      />
      
      <InputArea 
        onSendMessage={sendMessage} 
        isTyping={isTyping}
        disabled={isLoading.sending}
      />
    </ChatViewContainer>
  );
};

// Styled components
const ChatViewContainer = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
  background-color: var(--color-surface);
  position: relative;
`;

export default ChatView;