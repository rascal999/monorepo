import React, { useState, useRef } from 'react';
import { useKgraph } from './hooks/useKgraph';
import CytoscapeComponent from 'react-cytoscapejs';
import './App.css';

function NavigationPanel({ graphs, onCreateGraph, onOpenGraph, onDeleteGraph, onClearData, onOpenSettings }) {
  return (
    <div className="navigation-panel">
      <div className="panel-header">
        <h2>Graphs</h2>
        <button onClick={() => onCreateGraph('New Graph')}>Create New</button>
      </div>
      
      <div className="graph-list">
        {graphs.map(graph => (
          <div key={graph.id} className="graph-item">
            <span onClick={() => onOpenGraph(graph.id)}>{graph.title}</span>
            <button onClick={() => onDeleteGraph(graph.id)}>Delete</button>
          </div>
        ))}
      </div>
      
      <div className="panel-footer">
        <button onClick={onClearData}>Clear All Data</button>
        <button onClick={onOpenSettings}>Settings</button>
      </div>
    </div>
  );
}

function GraphPanel({ currentGraph, viewport, onCreateNode, onSelectNode }) {
  const cyRef = useRef(null);

  const cyStyle = [
    {
      selector: 'node',
      style: {
        'background-color': '#666',
        'label': 'data(label)'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 3,
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle'
      }
    }
  ];

  const handleClick = (event) => {
    const position = event.position;
    onCreateNode(position);
  };

  return (
    <div className="graph-panel">
      {currentGraph ? (
        <CytoscapeComponent
          elements={currentGraph.elements}
          style={{ width: '100%', height: '100%' }}
          stylesheet={cyStyle}
          cy={(cy) => { cyRef.current = cy; }}
          zoom={viewport.zoom}
          pan={viewport.position}
          onClick={handleClick}
        />
      ) : (
        <div className="no-graph">
          <p>No graph selected</p>
          <p>Create a new graph or select an existing one</p>
        </div>
      )}
    </div>
  );
}

function PropertiesPanel({ selectedNode, chatSession, onStartChat, onSendMessage, onCloseChat }) {
  const [activeTab, setActiveTab] = useState('properties');
  const [message, setMessage] = useState('');

  return (
    <div className="properties-panel">
      <div className="panel-tabs">
        <button 
          className={activeTab === 'properties' ? 'active' : ''} 
          onClick={() => setActiveTab('properties')}
        >
          Properties
        </button>
        <button 
          className={activeTab === 'chat' ? 'active' : ''} 
          onClick={() => {
            setActiveTab('chat');
            if (!chatSession) onStartChat();
          }}
        >
          Chat
        </button>
      </div>

      {activeTab === 'properties' && selectedNode && (
        <div className="properties-content">
          <h3>Node Properties</h3>
          <div className="property">
            <label>ID:</label>
            <span>{selectedNode.id}</span>
          </div>
          {Object.entries(selectedNode.data).map(([key, value]) => (
            <div key={key} className="property">
              <label>{key}:</label>
              <span>{value}</span>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'chat' && (
        <div className="chat-content">
          <div className="chat-messages">
            {chatSession?.messages.map((msg, index) => (
              <div key={index} className="message">
                {msg}
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && message.trim()) {
                  onSendMessage(message);
                  setMessage('');
                }
              }}
            />
            <button 
              onClick={() => {
                if (message.trim()) {
                  onSendMessage(message);
                  setMessage('');
                }
              }}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const {
    viewport,
    graphs,
    currentGraph,
    selectedNode,
    chatSession,
    createGraph,
    openGraph,
    deleteGraph,
    clearAllData,
    openSettings,
    createNode,
    selectNode,
    startChat,
    sendMessage,
    closeChat,
  } = useKgraph();

  return (
    <div className="app">
      <NavigationPanel
        graphs={graphs}
        onCreateGraph={createGraph}
        onOpenGraph={openGraph}
        onDeleteGraph={deleteGraph}
        onClearData={clearAllData}
        onOpenSettings={openSettings}
      />
      
      <GraphPanel
        currentGraph={currentGraph}
        viewport={viewport}
        onCreateNode={createNode}
        onSelectNode={selectNode}
      />
      
      <PropertiesPanel
        selectedNode={selectedNode}
        chatSession={chatSession}
        onStartChat={startChat}
        onSendMessage={sendMessage}
        onCloseChat={closeChat}
      />
    </div>
  );
}

export default App;
