import { useState, useRef } from 'react';

function ChatInput({ onSendMessage, isLoading }) {
  const [inputText, setInputText] = useState('');
  const mouseDownPos = useRef(null);

  const handleSend = () => {
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText('');
  };

  return (
    <div className="p-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          className="flex-1 px-3 py-2 bg-[var(--node-bg)] border border-[var(--border)] rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          onMouseDown={(e) => {
            mouseDownPos.current = { x: e.clientX, y: e.clientY };
          }}
          onMouseMove={(e) => {
            if (mouseDownPos.current) {
              const dx = Math.abs(e.clientX - mouseDownPos.current.x);
              const dy = Math.abs(e.clientY - mouseDownPos.current.y);
              // If mouse has moved more than 5px in any direction, consider it a drag
              if (dx > 5 || dy > 5) {
                e.currentTarget.blur();
                e.preventDefault();
              }
            }
          }}
          onMouseUp={() => {
            mouseDownPos.current = null;
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatInput;
