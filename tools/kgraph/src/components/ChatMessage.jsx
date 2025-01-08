import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

// Helper function to process text nodes
const processTextNode = (node, handleWordClick, selectedWords) => {
  if (typeof node === 'string') {
    // Split text into words, preserving phrases in parentheses
    const words = node.split(/\s+(?![^(]*\))/);
    return words.filter(word => word).map((word, index) => {
      // Check if word is wrapped in parentheses
      const match = word.match(/^\((.*?)\)([.,!?:])?$/);
      
      if (match) {
        // Split inner content into individual words
        const innerContent = match[1];
        const punctuation = match[2] || '';
        const innerWords = innerContent.split(/\s+/);
        
        return (
          <span key={index}>
            {'('}
            {innerWords.map((innerWord, innerIndex) => {
              // Handle special characters like & and +
              if (['&', '+', '/', '\\'].includes(innerWord)) {
                return <span key={innerIndex}>{innerWord} </span>;
              }
              
              // Clean individual word
              const cleanInnerWord = innerWord.replace(/[.,!?:]$/g, '');
              
              return (
                <span key={innerIndex}>
                  <span
                    onClick={(e) => handleWordClick(cleanInnerWord, e)}
                    className={`cursor-pointer hover:text-blue-500 hover:underline ${
                      selectedWords.includes(cleanInnerWord) 
                        ? 'bg-blue-100 text-blue-500' 
                        : ''
                    }`}
                  >
                    {innerWord}
                  </span>
                  {innerIndex < innerWords.length - 1 ? ' ' : ''}
                </span>
              );
            })}
            {')'}
            {punctuation}
            {index < words.length - 1 ? ' ' : ''}
          </span>
        );
      }

      // Remove parentheses and trailing punctuation, preserving content inside
      const cleanWord = word.replace(/\((.*?)\)/g, '$1').replace(/[.,!?:]$/g, '');

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
  const [isValid, setIsValid] = useState(false);

  // Validate message on mount and update
  useEffect(() => {
    // Skip validation if message is not yet available
    if (!message) return;

    const valid = Boolean(
      message.content && 
      typeof message.content === 'string' && 
      message.content.trim().length > 0
    );

    console.log('[ChatMessage] Validating message:', {
      role: message.role,
      contentLength: message.content?.length,
      contentType: typeof message.content,
      isValid: valid,
      nodeId
    });

    setIsValid(valid);
  }, [message, nodeId]);

  // Return null if message is not yet available
  if (!message) return null;

  // Return null if message is invalid
  if (!isValid) {
    console.debug('[ChatMessage] Message not yet valid:', {
      hasContent: Boolean(message.content),
      contentType: typeof message.content
    });
    return null;
  }

  const handleWordClick = (word, event) => {
    if (!nodeId) {
      console.warn('[ChatMessage] No nodeId provided for word click');
      return;
    }
    
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
