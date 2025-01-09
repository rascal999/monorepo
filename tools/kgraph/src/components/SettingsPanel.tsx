import React from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { setTheme, setAIModel, closeSettings, type AIModel } from '../store/slices/uiSlice';
import type { Theme } from '../store/types';

const SettingsPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const currentTheme = useAppSelector(state => state.ui.theme);
  const currentModel = useAppSelector(state => state.ui.aiModel);
  const currentTab = useAppSelector(state => state.ui.settingsTab);

  const handleThemeChange = (theme: Theme) => {
    dispatch(setTheme(theme));
  };

  const handleModelChange = (model: AIModel) => {
    dispatch(setAIModel(model));
  };

  return (
    <div className="settings-panel">
      <div className="settings-header">
        <h2>Settings</h2>
        <button 
          className="close-button"
          onClick={() => dispatch(closeSettings())}
        >
          ×
        </button>
      </div>

      <div className="settings-tabs">
        <button 
          className={`tab ${currentTab === 'general' ? 'active' : ''}`}
        >
          General
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

            <div className="setting-group">
              <h3>AI Model</h3>
              <div className="model-buttons">
                <button
                  className={`button ${currentModel === 'gpt-3.5-turbo' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => handleModelChange('gpt-3.5-turbo')}
                >
                  GPT-3.5 Turbo
                </button>
                <button
                  className={`button ${currentModel === 'gpt-4' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => handleModelChange('gpt-4')}
                >
                  GPT-4
                </button>
                <button
                  className={`button ${currentModel === 'claude-2' ? 'button-primary' : 'button-secondary'}`}
                  onClick={() => handleModelChange('claude-2')}
                >
                  Claude 2
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPanel;
