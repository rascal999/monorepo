import { streamOpenRouterResponse } from './api.js';
import { wrapWordsInClickableSpans } from './utils.js';
import { getData } from '../../data.js';

// Initialize chat history from localStorage or use default
let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || {};
let currentNodeId = null;

export async function sendMessage(input) {
  if (!currentNodeId) return;

  const message = input.value.trim();
  if (!message) return;

  // Add user message
  addChatMessage(currentNodeId, message, 'user');
  input.value = '';

  try {
    // Create temporary message for streaming
    const history = document.getElementById('chat-history');
    const tempMsg = document.createElement('div');
    tempMsg.className = 'chat-message ai streaming';
    history.appendChild(tempMsg);
    history.scrollTop = history.scrollHeight;

    // Get chat history for context
    const nodeChats = chatHistory[currentNodeId] || [];
    const messages = nodeChats.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
    messages.push({ role: 'user', content: message });

    // Stream AI response
    const response = await streamOpenRouterResponse(messages);
    
    // Add AI response to chat history
    addChatMessage(currentNodeId, response, 'assistant');
    
    // Remove temporary streaming message
    tempMsg.remove();
  } catch (error) {
    console.error('Error getting AI response:', error);
    addChatMessage(currentNodeId, 'Error: Failed to get AI response', 'error');
  }
}

async function getInitialDescription(nodeId) {
  try {
    // Get node name from graph data
    const graphData = getData();
    const node = graphData.nodes.find(n => n.id === nodeId);
    if (!node) return;

    // Create temporary message for streaming
    const history = document.getElementById('chat-history');
    const tempMsg = document.createElement('div');
    tempMsg.className = 'chat-message ai streaming';
    history.appendChild(tempMsg);
    history.scrollTop = history.scrollHeight;

    // Request initial description
    const messages = [{
      role: 'user',
      content: `Provide a short and concise description of "${node.name}". Keep it brief and focused.`
    }];

    // Stream AI response
    const response = await streamOpenRouterResponse(messages);
    
    // Add description request and response to chat history
    chatHistory[nodeId] = [
      { role: 'user', content: messages[0].content },
      { role: 'assistant', content: response }
    ];
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    
    // Update display
    displayChat(nodeId, true);
    
    // Remove temporary streaming message
    tempMsg.remove();
  } catch (error) {
    console.error('Error getting initial description:', error);
    chatHistory[nodeId] = [
      { role: 'error', content: 'Error: Failed to get initial description' }
    ];
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    displayChat(nodeId, true);
  }
}

export function displayChat(nodeId, scrollToBottom = false) {
  currentNodeId = nodeId;
  window.currentNodeId = nodeId; // Make available globally for UI
  const chatDiv = document.getElementById('chat-history');
  if (!chatDiv) return; // Guard against missing element

  // Initialize chat history for new nodes
  if (!chatHistory[nodeId]) {
    chatHistory[nodeId] = [];
    getInitialDescription(nodeId);
    return;
  }

  // Display existing chat history
  chatDiv.innerHTML = chatHistory[nodeId].map(msg => `
    <div class="chat-message ${msg.role}">
      ${wrapWordsInClickableSpans(msg.content)}
    </div>
  `).join('') || '<div class="detail-item">No chat history</div>';

  // Scroll to bottom if requested (e.g., after sending a message)
  if (scrollToBottom) {
    chatDiv.scrollTop = chatDiv.scrollHeight;
  }
}

export function addChatMessage(nodeId, message, role = 'user') {
  if (!nodeId || !message) return;
  
  // Initialize chat history for new nodes
  if (!chatHistory[nodeId]) {
    chatHistory[nodeId] = [];
  }
  
  // Add message to chat history
  chatHistory[nodeId].push({ role, content: message });
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
  
  // Update display if chat tab is active
  if (document.querySelector('.tab-button[data-tab="chat"]').classList.contains('active')) {
    displayChat(nodeId, true);
  }
}
