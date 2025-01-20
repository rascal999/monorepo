import { initializeChatInput } from './chat.js';

export function initializeTabs() {
  const tabButtons = document.querySelectorAll('.tab-button');
  tabButtons.forEach(button => {
    button.addEventListener('click', () => switchTab(button.dataset.tab));
  });

  // Initialize chat input after tabs are set up
  initializeChatInput();
}

export function switchTab(tabName) {
  // Update active states for buttons
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });

  // Update active states for panels
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `${tabName}-tab`);
  });

  // Ensure chat container is properly positioned when switching to chat tab
  if (tabName === 'chat') {
    const chatTab = document.getElementById('chat-tab');
    if (!chatTab.querySelector('.chat-container')) {
      initializeChatInput();
    }
  }
}
