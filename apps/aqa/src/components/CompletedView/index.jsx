import React from 'react';
import CompletionScreen from '../CompletionScreen/index.jsx';

const CompletedView = ({
  currentQuestion,
  totalQuestions,
  markedQuestions,
  handleNavigate,
  score,
  handleRestart,
  onSelectNew,
  userAnswers,
  averageAnswerTime,
  quiz
}) => {
  return (
    <div className="app-container">
      <div className="quiz-container">
        <CompletionScreen
          score={score}
          totalQuestions={totalQuestions}
          onRestart={handleRestart}
          onSelectNew={onSelectNew}
          userAnswers={userAnswers}
          averageAnswerTime={averageAnswerTime}
          quiz={quiz}
        />
      </div>
    </div>
  );
};

export default CompletedView;
