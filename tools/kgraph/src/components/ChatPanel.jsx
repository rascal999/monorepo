import { useRef, useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

function ChatPanel({ messages: propMessages, isLoading, nodeId, nodeLabel, nodeData, onSendMessage, onWordClick, handleGetDefinition }) {
  const chatEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const [prevNodeId, setPrevNodeId] = useState(nodeId);
  const [localMessages, setLocalMessages] = useState(nodeData?.chat || []);

  const [streamingMessage, setStreamingMessage] = useState(null);

  // Handle node switching and message updates
  useEffect(() => {
    // Handle node switching
    if (nodeId !== prevNodeId) {
      setPrevNodeId(nodeId);
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = 0;
      }
      setStreamingMessage(null);
    }

    // Always update local messages from nodeData
    setLocalMessages(nodeData?.chat || []);
  }, [nodeId, prevNodeId, nodeData?.chat]);

  // Handle message sending with streaming
  const handleSendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    setLocalMessages(prev => [...prev, userMessage]);
    
    // Scroll to bottom after sending user message
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    
    // Create placeholder for streaming response
    setStreamingMessage({ role: 'assistant', content: '' });
    
    // Call onSendMessage with streaming callback
    await onSendMessage(content, (update) => {
      if (update.success) {
        setStreamingMessage(update.message);
      }
    });
    
    // Store current scroll position
    const scrollPosition = chatContainerRef.current?.scrollTop;
    
    // Add final message to localMessages before clearing streaming
    if (streamingMessage) {
      setLocalMessages(prev => [...prev, streamingMessage]);
    }
    
    // Clear streaming message in next frame after localMessages is updated
    requestAnimationFrame(() => {
      setStreamingMessage(null);
      
      // Restore scroll position after all updates
      if (chatContainerRef.current && scrollPosition !== undefined) {
        chatContainerRef.current.scrollTop = scrollPosition;
      }
    });
  };

  // Combine regular messages with streaming message if present
  const allMessages = streamingMessage 
    ? [...localMessages, streamingMessage]
    : localMessages;
    
  const hasMessages = allMessages.length > 0;
  const isLoadingDefinition = Boolean(nodeData?.isLoadingDefinition);
  const showLoading = isLoadingDefinition && !hasMessages;
  const showButton = !nodeData?.chat?.length && !showLoading && nodeId;

  // Log state for debugging
  useEffect(() => {
    console.log('ChatPanel state:', {
      messages: allMessages,
      hasMessages,
      isLoading,
      isLoadingDefinition,
      showLoading,
      showButton,
      nodeData,
      nodeId,
      streaming: Boolean(streamingMessage)
    });
  }, [allMessages, hasMessages, isLoading, isLoadingDefinition, showLoading, showButton, nodeData, nodeId, streamingMessage]);

  return (
    <div className="relative flex flex-col h-full">
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-auto"
      >
        <div className="p-4 pb-20 space-y-4">
          {showButton && (
            <div className="flex justify-center">
              <button
                onClick={() => handleGetDefinition({ id: nodeId, data: { label: nodeLabel } })}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Get Definition
              </button>
            </div>
          )}
          {allMessages.map((message, index) => (
            <ChatMessage 
              key={index} 
              message={message} 
              onWordClick={onWordClick}
              nodeId={nodeId}
            />
          ))}
          {showLoading && (
            <div className="p-3 rounded-lg bg-[var(--node-bg)] flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              {allMessages.length === 0 ? (
                <div>Fetching definition for "{nodeLabel}"...</div>
              ) : (
                <div>Thinking...</div>
              )}
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>
      <div className="sticky bottom-0 bg-[var(--bg)] border-t border-[var(--border)]">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default ChatPanel;
