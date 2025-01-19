import React from 'react';
import './styles.css';

const ErrorView = ({ error, onBack }) => {
  return (
    <div className="app-container">
      <div className="quiz-container">
        <div className="error-container">
          <h1>Error</h1>
          <p className="error-message">{error}</p>
          <button 
            className="back-button" 
            onClick={onBack}
          >
            Back to Quiz Selection
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorView;
