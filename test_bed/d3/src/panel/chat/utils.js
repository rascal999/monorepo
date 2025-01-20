// Track selected words
let selectedWords = new Set();
const MAX_WORDS = 5;

// Create node from selected words
function createNodeFromSelection() {
  if (selectedWords.size === 0) return;
  
  // Join words with spaces
  const nodeName = Array.from(selectedWords).join(' ');
  window.handleWordClick(nodeName);
  selectedWords.clear();
  
  // Update all word displays to clear selection state
  document.querySelectorAll('.chat-message').forEach(msg => {
    msg.innerHTML = wrapWordsInClickableSpans(msg.textContent);
  });
}

export function wrapWordsInClickableSpans(message) {
  return message.split(/\s+/).map(word => {
    const isSelected = selectedWords.has(word);
    const title = isSelected ? 'Double-click to create node' : 'Ctrl+click to select';
    return `<span 
      class="clickable-word ${isSelected ? 'selected' : ''}" 
      onclick="window.handleWordClick('${word.replace(/'/g, "\\'")}', event)"
      ondblclick="window.handleWordDoubleClick()"
      title="${title}"
    >${word}</span>`;
  }).join(' ');
}

export function handleWordSelection(word, event) {
  // Handle Ctrl+click for word selection
  if (event.ctrlKey || event.metaKey) {
    if (selectedWords.has(word)) {
      selectedWords.delete(word);
    } else if (selectedWords.size < MAX_WORDS) {
      selectedWords.add(word);
    }

    // Update all word displays to show selection state
    document.querySelectorAll('.chat-message').forEach(msg => {
      msg.innerHTML = wrapWordsInClickableSpans(msg.textContent);
    });
  } else {
    // Regular click creates node immediately
    window.handleWordClick(word);
  }
}

// Handle double click to create node from selection
export function handleWordDoubleClick() {
  if (selectedWords.size > 0) {
    createNodeFromSelection();
  }
}

// Handle Enter key to create node from selection
document.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && selectedWords.size > 0) {
    createNodeFromSelection();
  }
});
