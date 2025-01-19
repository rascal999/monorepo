import React from 'react';
import './styles.css';

const NavigationPanel = ({ isOpen, onClose, currentQuestion, totalQuestions, markedQuestions, onNavigate }) => {
  return (
    <div className={`navigation-panel ${isOpen ? 'open' : ''}`}>
      <button className="close-button" onClick={onClose}>×</button>
      <div className="panel-content">
        <h2>Questions</h2>
        <div className="questions-list">
          {Array.from({ length: totalQuestions }, (_, index) => (
            <button
              key={index}
              className={`question-item ${currentQuestion === index ? 'active' : ''} ${markedQuestions[index] ? 'marked' : ''}`}
              onClick={() => {
                onNavigate(index);
                onClose();
              }}
            >
              Question {index + 1}
              {markedQuestions[index] && <span className="marked-indicator">★</span>}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NavigationPanel;
