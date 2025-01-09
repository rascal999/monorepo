import React, { useState, useRef, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { createGraph, deleteGraph, clearAll, loadGraph } from '../store/slices/graphSlice';
import { openSettings } from '../store/slices/uiSlice';
import SettingsPanel from './SettingsPanel';

const NavigationPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const panelRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [width, setWidth] = useState(250);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging && panelRef.current) {
        const newWidth = e.clientX;
        // Clamp width between min (150px) and max (250px)
        setWidth(Math.min(Math.max(newWidth, 150), 250));
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const graphs = useAppSelector(state => state.graph.graphs);
  const currentGraph = useAppSelector(state => state.graph.currentGraph);
  const settingsOpen = useAppSelector(state => state.ui.settingsOpen);
  const loading = useAppSelector(state => state.ui.loading);
  const [newGraphTitle, setNewGraphTitle] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const handleCreateGraph = () => {
    if (newGraphTitle.trim()) {
      dispatch(createGraph({ title: newGraphTitle.trim() }));
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
    <div 
      ref={panelRef}
      className="navigation-panel"
      style={{ width: `${width}px` }}
    >
      <div className="nav-title">
        <div className="title-container">
          <div className="title-text">kgraph</div>
          <button 
            className="settings-button"
            onClick={() => dispatch(openSettings())}
          >
            ⚙️
          </button>
        </div>
      </div>
      <div 
        className="resize-handle"
        onMouseDown={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
      />
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
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleCreateGraph();
              }
            }}
          />
        </div>
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
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteGraph(graph.id);
              }}
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

        {settingsOpen && (
          <>
            <div className="settings-overlay" />
            <SettingsPanel />
          </>
        )}
      </div>
    </div>
  );
};

export default NavigationPanel;
