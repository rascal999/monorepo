import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const Root = () => {
  useEffect(() => {
    if (import.meta.env.DEV) {
      document.title = '[DEV] MCQ Quiz App';
    }
  }, []);

  return (
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<Root />);
