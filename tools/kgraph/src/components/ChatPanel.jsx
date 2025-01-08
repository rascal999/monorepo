import { useRef, useEffect, useState, useCallback } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

function ChatPanel({ messages: propMessages, isLoading, nodeId, nodeLabel, nodeData, onSendMessage, onWordClick, handleGetDefinition, updateNodeData }) {
  const chatEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const restoredRef = useRef(false);
  const [prevNodeId, setPrevNodeId] = useState(nodeId);
  const [localMessages, setLocalMessages] = useState(nodeData?.chat || []);
  const [streamingMessage, setStreamingMessage] = useState(null);
  
  // Calculate initial scroll position
  const initialScrollTop = nodeData?.chatScrollPosition ?? 0;

  // Update scroll position handler
  const updatePosition = useCallback(() => {
    if (!chatContainerRef.current || !nodeId) return;
    updateNodeData(nodeId, 'chatScrollPosition', chatContainerRef.current.scrollTop);
  }, [nodeId, updateNodeData]);

  // Handle scroll events with throttling and mouseleave
  useEffect(() => {
    if (!chatContainerRef.current) return;

    let lastUpdate = 0;
    let scrollTimeout;
    const THROTTLE_MS = 150; // Throttle to ~6 updates per second

    const handleScroll = () => {
      const now = Date.now();
      
      // Clear any pending scroll end timeout
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }

      // Set new scroll end timeout
      scrollTimeout = setTimeout(updatePosition, 100);

      // Skip if within throttle window
      if (now - lastUpdate < THROTTLE_MS) return;

      lastUpdate = now;
      updatePosition();
    };

    // Save position when mouse leaves the chat container
    const handleMouseLeave = () => {
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }
      updatePosition();
    };

    const container = chatContainerRef.current;
    container.addEventListener('scroll', handleScroll, { passive: true });
    container.addEventListener('mouseleave', handleMouseLeave);
    
    return () => {
      container.removeEventListener('scroll', handleScroll);
      container.removeEventListener('mouseleave', handleMouseLeave);
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }
    };
  }, [updatePosition]);

  // Handle node switching and message updates
  useEffect(() => {
    // Handle node switching
    if (nodeId !== prevNodeId) {
      // Save scroll position of previous node before switching
      if (prevNodeId && chatContainerRef.current) {
        updateNodeData(prevNodeId, 'chatScrollPosition', chatContainerRef.current.scrollTop);
      }
      
      setPrevNodeId(nodeId);
      setStreamingMessage(null);
      restoredRef.current = false;
    }

    // Always update local messages from nodeData
    setLocalMessages(nodeData?.chat || []);
  }, [nodeId, prevNodeId, nodeData?.chat, updateNodeData]);

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
  // Show loading only if we're loading and don't have any messages yet
  const showLoading = isLoadingDefinition && !hasMessages;
  // Show button only if we don't have chat data and aren't loading
  const showButton = !nodeData?.chat?.length && !isLoadingDefinition && nodeId;

  return (
    <div className="relative flex flex-col h-full">
      <div 
        ref={(el) => {
          if (el && !restoredRef.current) {
            chatContainerRef.current = el;
            el.scrollTop = initialScrollTop;
            restoredRef.current = true;
          }
        }}
        className="flex-1 overflow-auto"
        style={{ scrollBehavior: 'instant' }}
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
