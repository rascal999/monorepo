import { initializeTabs, switchTab } from './panel/tabs.js';
import { displayNodeProperties } from './panel/properties.js';
import { displayChat, initializeChatInput } from './panel/chat.js';

// Initialize panel sizes from localStorage or use defaults
const defaultSizes = {
  navPanel: 250,
  detailsPanel: 300
};

let panelSizes = JSON.parse(localStorage.getItem('panelSizes')) || defaultSizes;

export function initializePanels() {
  // Initialize tabs
  initializeTabs();

  initializeResizer(
    document.getElementById('nav-resizer'),
    document.getElementById('nav-panel'),
    'navPanel',
    '--nav-panel-width'
  );

  initializeResizer(
    document.getElementById('details-resizer'),
    document.getElementById('details-panel'),
    'detailsPanel',
    '--details-panel-width'
  );
}

function initializeResizer(resizer, panel, storageKey, cssVar) {
  let x = 0;
  let panelWidth = 0;

  function mouseDownHandler(e) {
    x = e.clientX;
    panelWidth = panel.getBoundingClientRect().width;
    document.addEventListener('mousemove', mouseMoveHandler);
    document.addEventListener('mouseup', mouseUpHandler);
  }

  function mouseMoveHandler(e) {
    const dx = e.clientX - x;
    const newWidth = Math.min(Math.max(panelWidth + (panel.id === 'nav-panel' ? dx : -dx), 
      panel.id === 'nav-panel' ? 150 : 200), 
      panel.id === 'nav-panel' ? 400 : 500);
    
    // Update CSS variable
    document.documentElement.style.setProperty(cssVar, `${newWidth}px`);
  }

  function mouseUpHandler() {
    document.removeEventListener('mousemove', mouseMoveHandler);
    document.removeEventListener('mouseup', mouseUpHandler);
    // Save new size to localStorage
    panelSizes[storageKey] = panel.getBoundingClientRect().width;
    localStorage.setItem('panelSizes', JSON.stringify(panelSizes));
  }

  resizer.addEventListener('mousedown', mouseDownHandler);
}

export function displayNodeDetails(node) {
  displayNodeProperties(node);
  displayChat(node.id);
  // Switch to chat tab by default
  switchTab('chat');
}

// Re-export chat functionality
export { addChatMessage } from './panel/chat.js';
