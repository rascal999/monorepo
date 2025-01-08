import { useRef, useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

function ChatPanel({ messages: propMessages, isLoading, nodeId, nodeLabel, nodeData, onSendMessage, onWordClick }) {
  const chatEndRef = useRef(null);
  const [localMessages, setLocalMessages] = useState([]);
  
  // Handle node switching and message updates
  useEffect(() => {
    console.log('[ChatPanel] Node data:', {
      nodeId,
      hasChat: Boolean(nodeData?.chat),
      chatLength: nodeData?.chat?.length,
      messages: nodeData?.chat?.map(m => ({
        role: m.role,
        contentLength: m.content?.length,
        preview: m.content?.substring(0, 50)
      }))
    });

    // Validate and update messages
    if (nodeData?.chat && Array.isArray(nodeData.chat)) {
      console.log('[ChatPanel] Setting valid messages:', nodeData.chat.length);
      setLocalMessages(nodeData.chat);
    } else {
      console.log('[ChatPanel] No valid messages, clearing');
      setLocalMessages([]);
    }
  }, [nodeId, nodeData?.chat]); // Only update when chat data changes

  // Handle message sending
  const handleSendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    setLocalMessages(prev => [...prev, userMessage]);
    
    try {
      await onSendMessage(content);
    } catch (error) {
      console.error('[ChatPanel] Error sending message:', error);
    }
  };

  return (
    <div className="relative flex flex-col h-full">
      <div className="flex-1 overflow-auto">
        <div className="p-4 pb-20 space-y-4">
          {localMessages.map((message, index) => (
            <ChatMessage 
              key={index} 
              message={message} 
              onWordClick={onWordClick}
              nodeId={nodeId}
            />
          ))}
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
