import { addNode, getSelectedNode, setSelectedNode } from '../../data.js';
import { updateGraph } from '../../graph/index.js';
import { displayNodeDetails } from '../../panel.js';
import { createChatContainer } from './ui.js';
import { displayChat } from './messages.js';
import { handleWordSelection, handleWordDoubleClick } from './utils.js';

function handleWordClick(word, event) {
  if (event) {
    // Handle Ctrl+click word selection
    handleWordSelection(word, event);
  } else {
    // Handle regular click or programmatic node creation
    const selectedNode = getSelectedNode();
    if (!selectedNode) {
      console.log('No node selected');
      return;
    }

    // Create new node with the clicked word/phrase
    const newNode = addNode(word);
    
    // Select the new node
    setSelectedNode(newNode);
    displayNodeDetails(newNode);
    
    // Update graph visualization
    updateGraph();
  }
}

export function initializeChatInput() {
  createChatContainer();
  // Make handlers available globally for onclick handlers
  window.handleWordClick = handleWordClick;
  window.handleWordDoubleClick = handleWordDoubleClick;
}

// Re-export necessary functions
export { displayChat };
