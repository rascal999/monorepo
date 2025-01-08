import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { createGraph, deleteGraph, clearAll, createNode, setTheme, setLoading, loadGraph } from '../store/slices/appSlice';
import { Theme } from '../store/types';

const NavigationPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const graphs = useAppSelector(state => {
    console.log('NavigationPanel: Current state:', state);
    return state.app.graphs;
  });
  const currentGraph = useAppSelector(state => state.app.currentGraph);
  const currentTheme = useAppSelector(state => state.app.theme);
  const loading = useAppSelector(state => state.app.loading);
  const [newGraphTitle, setNewGraphTitle] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const handleCreateGraph = () => {
    if (newGraphTitle.trim()) {
      dispatch(createGraph({ title: newGraphTitle.trim() }));
      // Create first node with same title as graph
      dispatch(createNode({
        label: newGraphTitle.trim(),
        position: { x: 0, y: 0 }
      }));
      setNewGraphTitle('');
    }
  };

  const handleDeleteGraph = (graphId: string) => {
    if (window.confirm('Are you sure you want to delete this graph?')) {
      dispatch(deleteGraph(graphId));
    }
  };

  const handleClearAll = () => {
    if (showConfirmClear) {
      dispatch(clearAll());
      setShowConfirmClear(false);
    } else {
      setShowConfirmClear(true);
    }
  };

  const filteredGraphs = graphs.filter(graph => 
    graph.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="navigation-panel">
      <div className="header">
        <div className="input-group">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search graphs..."
            className="search-input"
          />
        </div>
        <div className="input-group">
          <input
            type="text"
            value={newGraphTitle}
            onChange={(e) => setNewGraphTitle(e.target.value)}
            placeholder="New graph title..."
          />
        </div>
        <button 
          className="button button-primary"
          onClick={handleCreateGraph}
          disabled={!newGraphTitle.trim()}
        >
          Create New Graph
        </button>
      </div>

      <div className="graph-list">
        {filteredGraphs.map(graph => (
          <div 
            key={graph.id}
            className={`graph-item ${currentGraph?.id === graph.id ? 'active' : ''}`}
            style={{
              padding: '8px',
              cursor: 'pointer',
              backgroundColor: currentGraph?.id === graph.id ? 'var(--primary-color)' : 'transparent',
              color: currentGraph?.id === graph.id ? 'white' : 'inherit',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderRadius: '4px',
              marginBottom: '4px'
            }}
            onClick={() => {
              console.log('NavigationPanel: Clicking graph:', graph.id, graph.title);
              console.log('NavigationPanel: Current graphs:', graphs);
              console.log('NavigationPanel: Dispatching LOAD_GRAPH action');
              dispatch(loadGraph(graph.id));
            }}
          >
            <span>
              {graph.title}
              {loading.status && loading.graphId === graph.id && (
                <span style={{ marginLeft: '8px', fontSize: '12px' }}>Loading...</span>
              )}
            </span>
            <button
              onClick={() => handleDeleteGraph(graph.id)}
              style={{ padding: '4px 8px' }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="actions">
        <button 
          className="button button-secondary"
          onClick={handleClearAll}
          style={{ width: '100%', marginBottom: '8px' }}
        >
          {showConfirmClear ? 'Confirm Clear All Data' : 'Clear All Data'}
        </button>
        <button 
          className="button button-secondary"
          onClick={() => setShowSettings(!showSettings)}
          style={{ width: '100%' }}
        >
          Settings
        </button>

        {showSettings && (
          <div className="settings-panel" style={{ marginTop: '16px', padding: '16px', backgroundColor: 'var(--panel-background)' }}>
            <h3 style={{ marginBottom: '16px' }}>Settings</h3>
            <div className="input-group">
              <label>Theme</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className={`button ${currentTheme === 'light' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => dispatch(setTheme('light'))}
                >
                  Light
                </button>
                <button
                  className={`button ${currentTheme === 'dark' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => dispatch(setTheme('dark'))}
                >
                  Dark
                </button>
                <button
                  className="button button-secondary"
                  onClick={() => {
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    dispatch(setTheme(prefersDark ? 'dark' : 'light'));
                  }}
                >
                  System
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NavigationPanel;
