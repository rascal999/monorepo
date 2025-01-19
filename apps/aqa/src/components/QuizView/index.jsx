import React, { useEffect } from 'react';
import QuizQuestion from '../QuizQuestion';
import ProgressBar from '../ProgressBar';
import NavigationDots from '../NavigationDots';
import NavigationButtons from '../NavigationButtons';
const QuizView = ({
  currentQuestion,
  totalQuestions,
  markedQuestions,
  handleNavigate,
  quiz,
  answers,
  answerStatuses,
  showExplanation,
  handleAnswer,
  isMarked,
  toggleMarkQuestion,
  setCompleted
}) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return; // Don't handle navigation when typing
      }
      
      switch (event.key) {
        case 'ArrowLeft':
          if (currentQuestion > 0) {
            event.preventDefault();
            handleNavigate(currentQuestion - 1);
          }
          break;
        case 'ArrowRight':
          if (currentQuestion < totalQuestions - 1) {
            event.preventDefault();
            handleNavigate(currentQuestion + 1);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentQuestion, totalQuestions, handleNavigate]);

  return (
    <div className="app-container">
      <div className="quiz-container">
        <ProgressBar
          currentQuestion={currentQuestion}
          totalQuestions={totalQuestions}
          title={quiz.title}
        />

        <NavigationDots
          totalQuestions={totalQuestions}
          currentQuestion={currentQuestion}
          answers={answers}
          answerStatuses={answerStatuses}
          markedQuestions={markedQuestions}
          onNavigate={handleNavigate}
        />

        {/* Use key to ensure proper re-rendering */}
        <QuizQuestion
          key={`question-${quiz.questions[currentQuestion].id}-${currentQuestion}`}
          question={quiz.questions[currentQuestion]}
          showExplanation={showExplanation}
          answers={answers}
          currentQuestion={currentQuestion}
          onAnswer={handleAnswer}
          isMarked={isMarked}
          onToggleMark={toggleMarkQuestion}
          quizTitle={quiz.title}
        />

        <NavigationButtons
          onPrevious={() => handleNavigate(currentQuestion - 1)}
          onNext={() => handleNavigate(currentQuestion + 1)}
          isFirstQuestion={currentQuestion === 0}
          isLastQuestion={currentQuestion === totalQuestions - 1}
          onFinish={() => setCompleted(true)}
          answers={answers}
          totalQuestions={totalQuestions}
        />
      </div>
    </div>
  );
};

export default QuizView;
