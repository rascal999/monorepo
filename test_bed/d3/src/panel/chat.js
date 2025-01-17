// Initialize chat history from localStorage or use default
let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || {};
let currentNodeId = null;

function createChatInput() {
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

function sendMessage(input) {
  if (!currentNodeId) return;

  const message = input.value.trim();
  if (message) {
    addChatMessage(currentNodeId, message);
    input.value = '';
  }
}

function createChatContainer() {
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
  if (currentNodeId) {
    displayChat(currentNodeId);
  }
}

export function initializeChatInput() {
  createChatContainer();
}

export function displayChat(nodeId, scrollToBottom = false) {
  currentNodeId = nodeId;
  const chatDiv = document.getElementById('chat-history');
  if (!chatDiv) return; // Guard against missing element

  const nodeChats = chatHistory[nodeId] || [];
  chatDiv.innerHTML = nodeChats.map(msg => `
    <div class="chat-message">
      ${msg}
    </div>
  `).join('') || '<div class="detail-item">No chat history</div>';

  // Scroll to bottom if requested (e.g., after sending a message)
  if (scrollToBottom) {
    chatDiv.scrollTop = chatDiv.scrollHeight;
  }
}

export function addChatMessage(nodeId, message) {
  if (!nodeId) return;
  if (!chatHistory[nodeId]) {
    chatHistory[nodeId] = [];
  }
  chatHistory[nodeId].push(message);
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
  
  if (document.querySelector('.tab-button[data-tab="chat"]').classList.contains('active')) {
    displayChat(nodeId, true); // Scroll to bottom after adding message
  }
}
