import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Set document title based on environment
if (import.meta.env.MODE === 'development') {
  document.title = '[DEV] MCQ Quiz App';
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
