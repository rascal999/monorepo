import { useRef, useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

function ChatPanel({ messages, isLoading, nodeId, nodeLabel, onSendMessage, onWordClick }) {
  const chatEndRef = useRef(null);

  const chatContainerRef = useRef(null);
  const [prevMessages, setPrevMessages] = useState(messages);
  const [prevNodeId, setPrevNodeId] = useState(nodeId);

  useEffect(() => {
    // Handle node switching
    if (nodeId !== prevNodeId) {
      setPrevNodeId(nodeId);
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = 0;
      }
      return;
    }

    // Handle new messages
    if (messages?.length > (prevMessages?.length || 0)) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }

    setPrevMessages(messages);
  }, [nodeId, messages]);

  return (
    <div className="relative flex flex-col h-full">
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-auto"
>
        <div className="p-4 space-y-4">
          {messages?.map((message, index) => (
            <ChatMessage 
              key={index} 
              message={message} 
              onWordClick={onWordClick}
              nodeId={nodeId}
            />
          ))}
          {isLoading && (
            <div className="p-3 rounded-lg bg-[var(--node-bg)] flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              {!messages || messages.length === 0 ? (
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
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default ChatPanel;
