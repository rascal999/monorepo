import React from 'react';
import './styles.css';

const GeneratingQuizView = ({ topic }) => {
  return (
    <div className="generating-container">
      <div className="generating-spinner"></div>
      <div className="generating-content">
        <h2>Generating Quiz</h2>
        <div className="generating-steps">
          <div className="step">
            <span className="step-label">Topic:</span>
            <span className="step-value">{topic}</span>
          </div>
          <div className="step">
            <span className="step-label">Status:</span>
            <span className="step-value">Creating questions and answers...</span>
          </div>
        </div>
        <p className="generating-note">This may take a few moments</p>
      </div>
    </div>
  );
};

export default GeneratingQuizView;
