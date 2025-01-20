import { sendMessage } from './messages.js';
import { displayChat } from './messages.js';

export function createChatInput() {
  const chatInput = document.createElement('div');
  chatInput.className = 'chat-input';

  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Type a message...';

  const sendButton = document.createElement('button');
  sendButton.textContent = 'Send';

  chatInput.appendChild(input);
  chatInput.appendChild(sendButton);

  // Send message on button click
  sendButton.addEventListener('click', () => {
    sendMessage(input);
  });

  // Send message on Enter key
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage(input);
    }
  });

  return chatInput;
}

export function createChatContainer() {
  // Create chat history
  const history = document.createElement('div');
  history.id = 'chat-history';

  // Create input
  const input = createChatInput();

  // Add both to chat tab
  const chatTab = document.getElementById('chat-tab');
  chatTab.innerHTML = ''; // Clear existing content
  chatTab.appendChild(history);
  chatTab.appendChild(input);

  // Display current node's chat history if any
  if (window.currentNodeId) {
    displayChat(window.currentNodeId);
  }
}
