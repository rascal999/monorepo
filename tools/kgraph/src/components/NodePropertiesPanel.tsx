import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { 
  editNode, 
  openChat, 
  closeChat, 
  addMessage 
} from '../store/slices/appSlice';

type Tab = 'properties' | 'chat';

const NodePropertiesPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const selectedNode = useAppSelector(state => state.app.selectedNode);
  const chatSession = useAppSelector(state => state.app.chatSession);
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [chatInput, setChatInput] = useState('');

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
    if (!chatInput.trim()) return;

    dispatch(addMessage({
      role: 'user',
      content: chatInput.trim()
    }));
    setChatInput('');
  };

  // Handle tab change
  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab);
    if (tab === 'chat') {
      dispatch(openChat());
    } else {
      dispatch(closeChat());
    }
  };

  if (!selectedNode) {
    return (
      <div className="node-properties-panel">
        <div className="content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Select a node to view properties</p>
        </div>
      </div>
    );
  }

  return (
    <div className="node-properties-panel">
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
                onChange={(e) => dispatch(editNode({
                  id: selectedNode.id,
                  changes: { label: e.target.value }
                }))}
              />
            </div>

            {Object.entries(selectedNode.properties).map(([key, value]) => (
              <div key={key} className="input-group">
                <label>{key}</label>
                <input
                  type="text"
                  value={value}
                  onChange={(e) => handlePropertyChange(key, e.target.value)}
                />
              </div>
            ))}

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
              {chatSession.messages.map((message, index) => (
                <div
                  key={index}
                  className={`chat-message ${message.role}`}
                >
                  {message.content}
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
