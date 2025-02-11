import React, { useEffect, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { setTheme, setAIModel, closeSettings, setModelSearchQuery, fetchModelsStart, setSettingsTab } from '../store/slices/uiSlice';
import type { Theme } from '../store/types';

const formatTokenCount = (count: number): string => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${Math.round(count / 1000)}k`;
  }
  return count.toString();
};

const SettingsPanel: React.FC = () => {
  const panelRef = useRef<HTMLDivElement>(null);
  const dispatch = useAppDispatch();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        dispatch(closeSettings());
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dispatch]);

  const currentTheme = useAppSelector(state => state.ui.theme);
  const selectedModel = useAppSelector(state => state.ui.selectedModel);
  const aiModels = useAppSelector(state => state.ui.aiModels);
  const searchQuery = useAppSelector(state => state.ui.modelSearchQuery);
  const currentTab = useAppSelector(state => state.ui.settingsTab);
  const modelsLoading = useAppSelector(state => state.ui.modelsLoading);
  const modelsError = useAppSelector(state => state.ui.modelsError);

  useEffect(() => {
    dispatch(fetchModelsStart());
  }, [dispatch]);

  const handleThemeChange = (theme: Theme) => {
    dispatch(setTheme(theme));
  };

  const handleModelChange = (modelId: string) => {
    dispatch(setAIModel(modelId));
  };

  return (
    <div ref={panelRef} className="settings-panel">
      <div className="settings-header">
        <div className="settings-tabs">
          <button 
            className={`tab ${currentTab === 'general' ? 'active' : ''}`}
            onClick={() => dispatch(setSettingsTab('general'))}
          >
            General
          </button>
          <button 
            className={`tab ${currentTab === 'ai' ? 'active' : ''}`}
            onClick={() => dispatch(setSettingsTab('ai'))}
          >
            AI
          </button>
          <button 
            className={`tab ${currentTab === 'about' ? 'active' : ''}`}
            onClick={() => dispatch(setSettingsTab('about'))}
          >
            About
          </button>
        </div>
        <button 
          className="close-button"
          onClick={() => dispatch(closeSettings())}
        >
          ×
        </button>
      </div>

      <div className="settings-content">
        {currentTab === 'general' && (
          <div className="general-settings">
            <div className="setting-group">
              <h3>Theme</h3>
              <div className="theme-buttons">
                <button
                  className={`button ${currentTheme === 'light' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => handleThemeChange('light')}
                >
                  Light
                </button>
                <button
                  className={`button ${currentTheme === 'dark' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => handleThemeChange('dark')}
                >
                  Dark
                </button>
                <button
                  className="button button-secondary"
                  onClick={() => {
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    handleThemeChange(prefersDark ? 'dark' : 'light');
                  }}
                >
                  System
                </button>
              </div>
            </div>
          </div>
        )}
        {currentTab === 'ai' && (
          <div className="ai-settings">
            <div className="setting-group">
              <h3>AI Model</h3>
              <div className="model-search">
                <input
                  type="text"
                  placeholder="Search models..."
                  value={searchQuery}
                  onChange={(e) => dispatch(setModelSearchQuery(e.target.value))}
                  className="search-input"
                />
              </div>
              {modelsLoading ? (
                <div className="model-loading">Loading available models...</div>
              ) : modelsError ? (
                <div className="model-error">Error: {modelsError}</div>
              ) : (
                <div className="model-list">
                  {aiModels
                    .filter(model => 
                      model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                      model.provider.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                    .sort((a, b) => {
                      // Selected model goes first
                      if (a.id === selectedModel) return -1;
                      if (b.id === selectedModel) return 1;
                      
                      // Sort alphabetically by name
                      return a.name.localeCompare(b.name);
                    })
                    .map(model => (
                      <button
                        key={model.id}
                        className={`model-item ${selectedModel === model.id ? 'selected' : ''}`}
                        onClick={() => handleModelChange(model.id)}
                      >
                        <div className="model-info">
                          <span className="model-name">{model.name}</span>
                          <span className="model-provider">{model.provider}</span>
                        </div>
                        {model.context_length && (
                          <span className="model-context">
                            {formatTokenCount(model.context_length)} tokens
                          </span>
                        )}
                      </button>
                    ))}
                </div>
              )}
            </div>
          </div>
        )}
        {currentTab === 'about' && (
          <div className="about-settings">
            <div className="setting-group">
              <h3><span className="k-highlight">k</span>graph</h3>
              <div className="about-content">
                <p>Created by <a href="https://github.com/rascal999" target="_blank" rel="noopener noreferrer">Aidan Marlin</a></p>
                <div className="about-links">
                  <a href="https://github.com/rascal999/monorepo/tree/main/tools/kgraph" target="_blank" rel="noopener noreferrer">
                    View on GitHub
                  </a>
                  <a href="https://github.com/rascal999/monorepo/issues" target="_blank" rel="noopener noreferrer">
                    Provide Feedback
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPanel;
