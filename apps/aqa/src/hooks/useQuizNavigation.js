import { useState } from 'react';

export function useQuizNavigation(totalQuestions) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [showExplanation, setShowExplanation] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [markedQuestions, setMarkedQuestions] = useState(Array(totalQuestions).fill(false));

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1);
      return true;
    } else {
      setCompleted(true);
      return false;
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
      return true;
    }
    return false;
  };

  const handleNavigate = (index) => {
    if (index >= 0 && index < totalQuestions) {
      console.log('Navigation:', {
        from: currentQuestion,
        to: index,
        showExplanation
      });
      setCurrentQuestion(index);
      // Don't reset explanation - let QuizView control this based on answer state
    }
  };

  const toggleMarkQuestion = () => {
    const newMarkedQuestions = [...markedQuestions];
    newMarkedQuestions[currentQuestion] = !newMarkedQuestions[currentQuestion];
    setMarkedQuestions(newMarkedQuestions);
  };

  const resetNavigation = () => {
    setCurrentQuestion(0);
    setShowExplanation(false);
    setCompleted(false);
    setMarkedQuestions(Array(totalQuestions).fill(false));
  };

  return {
    currentQuestion,
    showExplanation,
    completed,
    markedQuestions,
    setShowExplanation,
    setCompleted,
    handleNext,
    handlePrevious,
    handleNavigate,
    toggleMarkQuestion,
    resetNavigation
  };
}
