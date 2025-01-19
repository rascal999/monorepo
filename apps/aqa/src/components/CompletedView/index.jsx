import React from 'react';
import CompletionScreen from '../CompletionScreen';
import NavigationPanel from '../NavigationPanel';
import HamburgerMenu from '../HamburgerMenu';

const CompletedView = ({
  isPanelOpen,
  setIsPanelOpen,
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
      <HamburgerMenu onClick={() => setIsPanelOpen(true)} />
      <NavigationPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        currentQuestion={currentQuestion}
        totalQuestions={totalQuestions}
        markedQuestions={markedQuestions}
        onNavigate={handleNavigate}
      />
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
