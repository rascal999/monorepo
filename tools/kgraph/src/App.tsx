import React, { useEffect } from 'react';
import { useAppSelector, useAppDispatch } from './store';
import { setTheme } from './store/slices/uiSlice';
import NavigationPanel from './components/NavigationPanel';
import GraphPanel from './components/GraphPanel';
import NodePropertiesPanel from './components/NodePropertiesPanel';
import './styles/App.css';

const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const error = useAppSelector(state => state.ui.error);

  useEffect(() => {
    // Check system preference for dark mode
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    dispatch(setTheme(prefersDark ? 'dark' : 'light'));

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      dispatch(setTheme(e.matches ? 'dark' : 'light'));
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [dispatch]);

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
