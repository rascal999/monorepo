import React from 'react';
import './styles.css';

const LoadingView = () => {
  return (
    <div className="app-container">
      <div className="quiz-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h1>Loading quiz...</h1>
        </div>
      </div>
    </div>
  );
};

export default LoadingView;
