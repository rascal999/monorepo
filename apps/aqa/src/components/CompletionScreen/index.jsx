import React from 'react';
import './styles.css';

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
      <h1>Quiz Completed!</h1>
      
      <div className="score-container">
        <div className="score">
          <span className="score-value">{percentage}%</span>
          <span className="score-details">
            {score} out of {totalQuestions} correct
          </span>
        </div>
        <div className="time-stats">
          <p>Average time per question: {formatTime(averageAnswerTime)}</p>
        </div>
      </div>

      <div className="answers-review">
        <h2>Review Your Answers</h2>
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
