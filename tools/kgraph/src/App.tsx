import React from 'react';
import { useAppSelector } from './store';
import NavigationPanel from './components/NavigationPanel';
import GraphPanel from './components/GraphPanel';
import NodePropertiesPanel from './components/NodePropertiesPanel';
import './styles/App.css';

const App: React.FC = () => {
  const error = useAppSelector(state => state.app.error);

  return (
    <div className="app">
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}
      <div className="panels-container">
        <NavigationPanel />
        <GraphPanel />
        <NodePropertiesPanel />
      </div>
    </div>
  );
};

export default App;
