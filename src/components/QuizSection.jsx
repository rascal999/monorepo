import { useState, useEffect } from 'react';
import { QuizHeader } from './QuizHeader';
import { QuestionNavigation } from './QuestionNavigation';
import { QuestionDisplay } from './QuestionDisplay';
import { QuizControls } from './QuizControls';

export function QuizSection({
  title,
  questions,
  currentQuestionIndex,
  userAnswers,
  revealedQuestions,
  isTimerRunning,
  onTimerTick,
  onOptionSelect,
  onRevealAnswers,
  onNextQuestion,
  onPreviousQuestion,
  onJumpToQuestion,
  onFinishQuiz,
  flaggedQuestions,
  onToggleFlag,
  showTimer,
  showAnswersStraightaway,
  hideAnswerFeedback,
  section,
  onRestart
}) {
  const [selectedOptionIndex, setSelectedOptionIndex] = useState(-1);
  const currentQuestion = questions[currentQuestionIndex];

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!currentQuestion) return;

      switch (e.key) {
        case 'ArrowRight':
          if (currentQuestionIndex < questions.length - 1) {
            onNextQuestion();
          }
          break;
        case 'ArrowLeft':
          if (currentQuestionIndex > 0) {
            onPreviousQuestion();
          }
          break;
        case 'ArrowUp':
          if (revealedQuestions.has(currentQuestionIndex)) {
            e.preventDefault(); // Prevent page scroll when cycling through answers
            setSelectedOptionIndex(prev => {
              const newIndex = prev <= 0 ? currentQuestion.options.length - 1 : prev - 1;
              return newIndex;
            });
          }
          break;
        case 'ArrowDown':
          if (revealedQuestions.has(currentQuestionIndex)) {
            e.preventDefault(); // Prevent page scroll when cycling through answers
            setSelectedOptionIndex(prev => {
              const newIndex = prev >= currentQuestion.options.length - 1 ? 0 : prev + 1;
              return newIndex;
            });
          }
          break;
        case ' ':
          if (!revealedQuestions.has(currentQuestionIndex) && !showAnswersStraightaway) {
            e.preventDefault(); // Prevent spacebar from scrolling
            onRevealAnswers();
          }
          break;
        case 'Enter':
          if (selectedOptionIndex !== -1 && revealedQuestions.has(currentQuestionIndex)) {
            onOptionSelect(selectedOptionIndex);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentQuestionIndex, questions.length, selectedOptionIndex, revealedQuestions, currentQuestion, onNextQuestion, onPreviousQuestion, onRevealAnswers, onOptionSelect, showAnswersStraightaway]);

  // Reset selected option when question changes
  useEffect(() => {
    setSelectedOptionIndex(-1);
  }, [currentQuestionIndex]);

  if (!currentQuestion) return null;

  return (
    <div className="section">
      <QuizHeader
        title={title}
        currentQuestionIndex={currentQuestionIndex}
        totalQuestions={questions.length}
        isTimerRunning={isTimerRunning}
        onTimerTick={onTimerTick}
        showTimer={showTimer}
        restartQuiz={onRestart}
      />

      <QuestionNavigation
        currentQuestionIndex={currentQuestionIndex}
        totalQuestions={questions.length}
        userAnswers={userAnswers}
        questions={questions}
        flaggedQuestions={flaggedQuestions}
        onJumpToQuestion={onJumpToQuestion}
        onToggleFlag={onToggleFlag}
        hideAnswerFeedback={hideAnswerFeedback}
        section={section}
      />

      <QuestionDisplay
        currentQuestionIndex={currentQuestionIndex}
        question={currentQuestion}
        userAnswers={userAnswers}
        revealedQuestions={revealedQuestions}
        onOptionSelect={onOptionSelect}
        onRevealAnswers={onRevealAnswers}
        selectedOptionIndex={selectedOptionIndex}
        showAnswersStraightaway={showAnswersStraightaway}
        hideAnswerFeedback={hideAnswerFeedback}
        section={section}
        quizTitle={title}
      />

      <QuizControls
        currentQuestionIndex={currentQuestionIndex}
        totalQuestions={questions.length}
        onPreviousQuestion={onPreviousQuestion}
        onNextQuestion={onNextQuestion}
        onFinishQuiz={onFinishQuiz}
      />
    </div>
  );
}
