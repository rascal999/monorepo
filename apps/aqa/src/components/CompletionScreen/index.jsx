import React from 'react';
import './styles/index.css';
import './styles/score.css';
import './styles/answers.css';

const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const CompletionScreen = ({ 
  score, 
  totalQuestions, 
  onRestart, 
  onSelectNew,
  userAnswers,
  averageAnswerTime,
  quiz
}) => {
  const percentage = Math.round((score / totalQuestions) * 100);

  // Sort answers by their original question index
  const sortedAnswers = [...userAnswers]
    .filter(answer => answer !== null)
    .sort((a, b) => a.originalQuestionIndex - b.originalQuestionIndex);

  return (
    <div className="completion-screen">
      <div className="completion-header">
        <h1>Quiz Completed!</h1>
        <p className="completion-subtitle">Here's your detailed quiz performance:</p>
      </div>
      
      <div className="score-container">
        <div className="score">
          <span className="score-value">{percentage}%</span>
          <span className="score-details">
            {score} out of {totalQuestions} correct
          </span>
        </div>
        <div className="time-stats">
          <h3>Time Statistics</h3>
          <p>Average time per question: {formatTime(averageAnswerTime)}</p>
          <p>Total questions answered: {userAnswers.filter(a => a !== null).length}</p>
        </div>
      </div>

      <div className="summary-stats">
        <h2>Detailed Statistics</h2>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Correct Answers:</span>
            <span className="stat-value">{score}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Incorrect Answers:</span>
            <span className="stat-value">{totalQuestions - score}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Accuracy:</span>
            <span className="stat-value">{percentage}%</span>
          </div>
        </div>
      </div>

      <div className="answers-review">
        <h2>Question-by-Question Review</h2>
        {sortedAnswers.map((userAnswer, index) => {
          const question = quiz.questions.find(q => q.id === userAnswer.questionId);

          return (
            <div key={question.id} className="answer-review-item">
              <h3>Question {index + 1}</h3>
              <p className="question-text">{question.question_text}</p>
              
              <div className="answer-details">
                <div className={`user-answer ${userAnswer.isCorrect ? 'correct' : 'incorrect'}`}>
                  <strong>Your answer:</strong> {userAnswer.answerText}
                  <span className="answer-time">
                    Time taken: {formatTime(userAnswer.timeTaken)}
                  </span>
                </div>
                
                {!userAnswer.isCorrect && (
                  <div className="correct-answer">
                    <strong>Correct answer:</strong> {userAnswer.correctAnswer}
                  </div>
                )}
              </div>

              <div className="explanation">
                <strong>Explanation:</strong>
                <p>{userAnswer.explanation}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="completion-buttons">
        <button onClick={onRestart} className="restart-button">
          Restart Quiz (New Order)
        </button>
        <button onClick={onSelectNew} className="select-new-button">
          Try Another Quiz
        </button>
      </div>
    </div>
  );
};

export default CompletionScreen;
