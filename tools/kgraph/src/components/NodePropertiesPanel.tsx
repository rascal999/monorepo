import React, { useState, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { editNode, createWordNode } from '../store/slices/nodeSlice';
import { addMessage } from '../store/slices/chatSlice';
import { updatePanelWidth } from '../store/slices/uiSlice';
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

  // Track chat history separately to force re-render on changes
  const chatHistory = useAppSelector(
    React.useCallback((state) => {
      const node = state.node.selectedNode;
      return node?.properties.chatHistory || [];
    }, [])
  );
  const panelWidth = useAppSelector(state => state.ui.panelWidth);
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [chatInput, setChatInput] = useState('');
  const [isResizing, setIsResizing] = useState(false);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const newWidth = window.innerWidth - e.clientX;
    // Limit minimum and maximum width
    const clampedWidth = Math.min(Math.max(newWidth, 300), 800);
    dispatch(updatePanelWidth(clampedWidth));
  }, [isResizing, dispatch]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  React.useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

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

  // Handle word click
  const handleWordClick = (word: string) => {
    if (!selectedNode || !currentGraph) {
      console.warn('Cannot create word node: No selected node or current graph', {
        selectedNode: !!selectedNode,
        currentGraph: !!currentGraph
      });
      return;
    }
    
    // Calculate position for new node relative to parent
    const offset = 150; // pixels
    const angle = (Math.PI * 2 * Math.random()); // random angle
    const newPosition = {
      x: selectedNode.position.x + offset * Math.cos(angle),
      y: selectedNode.position.y + offset * Math.sin(angle)
    };
    
    console.log('Creating word node', {
      word,
      parentNodeId: selectedNode.id,
      graphId: currentGraph.id
    });
    
    dispatch(createWordNode({
      parentNodeId: selectedNode.id,
      word: word,
      position: newPosition,
      graphId: currentGraph.id // graphId is now required
    }));
  };

  if (!selectedNode) {
    return (
      <div className="node-properties-panel" style={{ width: panelWidth }}>
        <div 
          className={`resize-handle ${isResizing ? 'resizing' : ''}`}
          onMouseDown={handleMouseDown}
        />
        <div className="content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Select a node to view properties</p>
        </div>
      </div>
    );
  }

  return (
    <div className="node-properties-panel" style={{ width: panelWidth }}>
      <div 
        className={`resize-handle ${isResizing ? 'resizing' : ''}`}
        onMouseDown={handleMouseDown}
      />
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
          <div className="chat-content">
            <div className="chat-messages">
              {chatHistory.map((message: ChatMessage, index: number) => (
                <div
                  key={index}
                  className={`chat-message ${message.role}`}
                >
                  {message.content.split(/\s+/).map((word, wordIndex, words) => (
                    <React.Fragment key={wordIndex}>
                      <span
                        className="clickable-word"
                        onClick={() => handleWordClick(word)}
                      >
                        {word}
                      </span>
                      {wordIndex < words.length - 1 ? ' ' : ''}
                    </React.Fragment>
                  ))}
                </div>
              ))}
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
                disabled={!chatInput.trim()}
              >
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NodePropertiesPanel;
