import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/global.css';
import App from './components/App';
import { ThemeProvider } from './context/ThemeContext';
import { AppProvider } from './context/AppContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider>
      <AppProvider>
        <App />
      </AppProvider>
    </ThemeProvider>
  </React.StrictMode>
);