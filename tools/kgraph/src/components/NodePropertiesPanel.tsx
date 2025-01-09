import React, { useState, useRef, useCallback, useMemo } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { editNode, createWordNode } from '../store/slices/nodeSlice';
import { addMessage } from '../store/slices/chatSlice';
import { addSelectedWord, removeSelectedWord, clearSelectedWords } from '../store/slices/uiSlice';
import type { Node } from '../store/types';

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

type Tab = 'properties' | 'chat';

const NodePropertiesPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const selectedNode = useAppSelector(
    React.useCallback((state) => {
      const node = state.node.selectedNode;
      if (!node) return null;
      return node;
    }, [])
  );

  const currentGraph = useAppSelector(
    React.useCallback((state) => state.graph.currentGraph, [])
  );

  // Track chat history, streaming state, and selected words
  const { chatHistory, streaming, selectedWords } = useAppSelector(
    React.useCallback((state) => ({
      chatHistory: state.node.selectedNode?.properties.chatHistory || [],
      streaming: state.chat.streaming,
      selectedWords: state.ui.selectedWords
    }), [])
  );

  const [width, setWidth] = useState(400);
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [chatInput, setChatInput] = useState('');
  const panelRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.pageX;
    const startWidth = width;

    const handleMouseMove = (e: MouseEvent) => {
      requestAnimationFrame(() => {
        const diff = startX - e.pageX;
        const newWidth = Math.min(Math.max(startWidth + diff, 300), 800);
        setWidth(newWidth);
      });
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [width]);

  // Handle property changes
  const handlePropertyChange = (key: string, value: string) => {
    if (!selectedNode) return;
    
    dispatch(editNode({
      id: selectedNode.id,
      changes: {
        properties: {
          ...selectedNode.properties,
          [key]: value
        }
      }
    }));
  };

  // Handle adding new property
  const handleAddProperty = () => {
    if (!selectedNode) return;
    
    const newKey = `property${Object.keys(selectedNode.properties).length + 1}`;
    
    dispatch(editNode({
      id: selectedNode.id,
      changes: {
        properties: {
          ...selectedNode.properties,
          [newKey]: ''
        }
      }
    }));
  };

  // Handle chat message send
  const handleSendMessage = () => {
    if (!chatInput.trim() || !selectedNode) return;
    
    dispatch(addMessage({
      nodeId: selectedNode.id,
      role: 'user',
      content: chatInput.trim()
    }));
    setChatInput('');
  };

  // Handle tab change
  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab);
  };

  // Clean word to only include alphanumeric, space, underscore and hyphen
  const cleanWord = useCallback((word: string) => {
    return word.replace(/[^a-zA-Z0-9\s_-]/g, '').trim();
  }, []);

  // Create a node at a random offset from the parent node
  const createNodeAtOffset = useCallback((word: string) => {
    if (!selectedNode || !currentGraph) return;

    const offset = 150; // pixels
    const angle = (Math.PI * 2 * Math.random()); // random angle
    const newPosition = {
      x: selectedNode.position.x + offset * Math.cos(angle),
      y: selectedNode.position.y + offset * Math.sin(angle)
    };

    dispatch(createWordNode({
      parentNodeId: selectedNode.id,
      word,
      position: newPosition,
      graphId: currentGraph.id
    }));
  }, [selectedNode, currentGraph, dispatch]);

  // Handle word click
  const handleWordClick = (e: React.MouseEvent, word: string) => {
    if (!selectedNode || !currentGraph) {
      console.warn('Cannot handle word click: No selected node or current graph', {
        selectedNode: !!selectedNode,
        currentGraph: !!currentGraph
      });
      return;
    }

    const cleanedWord = cleanWord(word);
    if (!cleanedWord) return; // Skip if word is empty after cleaning

    if (e.ctrlKey) {
      e.preventDefault();
      // Toggle word selection for multi-word nodes
      if (selectedWords.includes(cleanedWord)) {
        dispatch(removeSelectedWord(cleanedWord));
      } else {
        dispatch(addSelectedWord(cleanedWord));
      }
    } else {
      // Create single word node immediately on regular click
      createNodeAtOffset(cleanedWord);
    }
  };

  // Handle creating node from multiple selected words
  const handleCreateWordNode = useCallback(() => {
    if (!selectedNode || !currentGraph || selectedWords.length === 0) return;

    const combinedWord = selectedWords.map(cleanWord).filter(Boolean).join(' ');
    createNodeAtOffset(combinedWord);

    // Clear selected words after creating node
    dispatch(clearSelectedWords());
  }, [selectedNode, currentGraph, selectedWords, cleanWord, createNodeAtOffset, dispatch]);

  if (!selectedNode) {
    return (
      <div ref={panelRef} className="node-properties-panel" style={{ width }}>
        <div className="resize-handle" onMouseDown={handleMouseDown} />
        <div className="content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Select a node to view properties</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={panelRef} className="node-properties-panel" style={{ width }}>
      <div className="resize-handle" onMouseDown={handleMouseDown} />
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => handleTabChange('chat')}
        >
          Chat
        </button>
        <button
          className={`tab ${activeTab === 'properties' ? 'active' : ''}`}
          onClick={() => handleTabChange('properties')}
        >
          Properties
        </button>
      </div>

      <div className="content">
        {activeTab === 'properties' ? (
          <div className="properties-content">
            <div className="input-group">
              <label>Label</label>
              <input
                type="text"
                value={selectedNode.label}
                onChange={(e) => {
                  dispatch(editNode({
                    id: selectedNode.id,
                    changes: { label: e.target.value }
                  }));
                }}
              />
            </div>

            {Object.entries(selectedNode.properties)
              .filter(([key]) => key !== 'chatHistory')
              .map(([key, value]) => (
                <div key={key} className="input-group">
                  <label>{key}</label>
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => handlePropertyChange(key, e.target.value)}
                  />
                </div>
              ))
            }

            <button
              className="button button-secondary"
              onClick={handleAddProperty}
              style={{ marginTop: '16px' }}
            >
              Add Property
            </button>
          </div>
        ) : (
          <>
            <div className="chat-content">
              <div className="chat-messages">
                {chatHistory.slice(1).map((message: ChatMessage, index: number) => (
                  <div
                    key={index}
                    className={`chat-message ${message.role}`}
                  >
                    {message.content.split(/\s+/).map((word, wordIndex, words) => (
                      <React.Fragment key={wordIndex}>
                        <span
                          className={`clickable-word ${selectedWords.includes(word) ? 'selected' : ''}`}
                          onClick={(e) => handleWordClick(e, word)}
                        >
                          {word}
                        </span>
                        {wordIndex < words.length - 1 ? ' ' : ''}
                      </React.Fragment>
                    ))}
                  </div>
                ))}
                {streaming.inProgress && streaming.nodeId === selectedNode?.id && (
                  <div className="chat-message assistant streaming">
                    {streaming.currentResponse.split(/\s+/).map((word, wordIndex, words) => (
                      <React.Fragment key={wordIndex}>
                        <span 
                          className={`clickable-word ${selectedWords.includes(word) ? 'selected' : ''}`}
                          onClick={(e) => handleWordClick(e, word)}
                        >
                          {word}
                        </span>
                        {wordIndex < words.length - 1 ? ' ' : ''}
                      </React.Fragment>
                    ))}
                    <span className="streaming-cursor">▋</span>
                  </div>
                )}
                {streaming.error && streaming.nodeId === selectedNode?.id && (
                  <div className="chat-message error">
                    Error: {streaming.error}
                  </div>
                )}
              </div>
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage();
                  }
                }}
                placeholder="Type your message..."
              />
              <button
                className="button button-primary"
                onClick={handleSendMessage}
                disabled={!chatInput.trim() || streaming.inProgress}
              >
                {streaming.inProgress ? 'Thinking...' : 'Send'}
              </button>
            </div>
          </>
        )}
      </div>

      {/* Selected words counter */}
      {selectedWords.length > 0 && (
        <div className="selected-words-counter">
          <span>{selectedWords.length} word{selectedWords.length !== 1 ? 's' : ''} selected</span>
          <button onClick={handleCreateWordNode}>Create Node</button>
          <button onClick={() => dispatch(clearSelectedWords())}>Clear</button>
        </div>
      )}
    </div>
  );
};

export default NodePropertiesPanel;
