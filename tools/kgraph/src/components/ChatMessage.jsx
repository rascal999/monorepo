import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

// Helper function to process text nodes
const processTextNode = (node, handleWordClick, selectedWords) => {
  if (typeof node === 'string') {
    // Split text into words, preserving phrases in parentheses
    const words = node.split(/\s+(?![^(]*\))/);
    return words.filter(word => word).map((word, index) => {
      // Remove parentheses and trailing punctuation, preserving content inside
      const cleanWord = word.replace(/\((.*?)\)/g, '$1').replace(/[.,!?:]$/g, '');
      
      // Check if word is wrapped in parentheses
      const match = word.match(/^\((.*)\)$/);
      if (match) {
        // For words in parentheses, only make the inner content clickable
        const innerContent = match[1];
        return (
          <span key={index}>
            {'('}
            <span
              onClick={(e) => handleWordClick(innerContent, e)}
              className={`cursor-pointer hover:text-blue-500 hover:underline ${
                selectedWords.includes(innerContent) 
                  ? 'bg-blue-100 text-blue-500' 
                  : ''
              }`}
            >
              {innerContent}
            </span>
            {')'}
            {index < words.length - 1 ? ' ' : ''}
          </span>
        );
      }

      // For regular words, make the whole word clickable but pass clean version
      return (
        <span key={index}>
          <span
            onClick={(e) => handleWordClick(cleanWord, e)}
            className={`cursor-pointer hover:text-blue-500 hover:underline ${
              selectedWords.includes(cleanWord) 
                ? 'bg-blue-100 text-blue-500' 
                : ''
            }`}
          >
            {word}
          </span>
          {index < words.length - 1 ? ' ' : ''}
        </span>
      );
    });
  }
  return node;
};

function ChatMessage({ message, onWordClick, nodeId }) {
  const [selectedWords, setSelectedWords] = useState([]);

  const handleWordClick = (word, event) => {
    if (!nodeId) return;
    
    // Remove parentheses and trailing punctuation, preserving content inside
    const cleanWord = word.replace(/\((.*?)\)/g, '$1').replace(/[.,!?:]$/g, '');
    
    if (event.ctrlKey || event.metaKey) {
      setSelectedWords(prev => {
        // If already selected, remove it
        if (prev.includes(cleanWord)) {
          return prev.filter(w => w !== cleanWord);
        }
        // Add word if under limit
        if (prev.length < 5) {
          return [...prev, cleanWord];
        }
        return prev;
      });
    } else {
      // Regular click - pass single word up
      onWordClick([cleanWord]);
      setSelectedWords([]); // Clear selection
    }
  };

  const renderContent = () => {
    if (message.role === 'assistant') {
      return (
        <div>
          <ReactMarkdown
            components={{
              // Custom renderer for text nodes to maintain word click functionality
              // Process text nodes in all elements
              p: ({ children }) => (
                <p>{React.Children.map(children, node => processTextNode(node, handleWordClick, selectedWords))}</p>
              ),
              strong: ({ children }) => (
                <span className="font-bold">
                  {React.Children.map(children, node => processTextNode(node, handleWordClick, selectedWords))}
                  {' '}
                </span>
              ),
              em: ({ children }) => (
                <span className="italic">
                  {React.Children.map(children, node => processTextNode(node, handleWordClick, selectedWords))}
                  {' '}
                </span>
              ),
              ul: ({ children }) => <ul className="list-disc ml-4 my-1 inline-block">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal ml-4 my-1 inline-block">{children}</ol>,
              li: ({ children }) => (
                <li className="my-1">
                  {React.Children.map(children, node => processTextNode(node, handleWordClick, selectedWords))}
                </li>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
          {selectedWords.length > 0 && (
            <button
              onClick={() => {
                onWordClick(selectedWords);
                setSelectedWords([]);
              }}
              className="mt-2 px-3 py-1 bg-blue-500 text-white rounded-lg text-sm"
            >
              Create node from {selectedWords.length} selected word{selectedWords.length > 1 ? 's' : ''}
            </button>
          )}
        </div>
      );
    }
    return message.content;
  };

  return (
    <div
      className={`p-3 rounded-lg ${
        message.role === 'assistant' ? 'bg-[var(--node-bg)]' : 'bg-blue-500 text-white'
      }`}
    >
      {renderContent()}
    </div>
  );
}

export default ChatMessage;
