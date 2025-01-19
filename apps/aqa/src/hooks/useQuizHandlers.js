import { useMemo } from 'react';

export function useQuizHandlers(state) {
  return useMemo(() => {
    const handleAnswerSubmit = (value) => {
      const currentQuizQuestion = state.quiz.questions[state.currentQuestion];
      console.log('handleAnswerSubmit:', {
        value,
        currentQuestion: state.currentQuestion,
        questionId: currentQuizQuestion.id,
        questionText: currentQuizQuestion.question_text,
        currentAnswers: state.answers
      });

      const correctAnswer = currentQuizQuestion.answers.find(a => a.is_correct);
      const timeTaken = state.recordAnswerTime(state.currentQuestion);

      // Use the stored original index
      const originalIndex = currentQuizQuestion.originalIndex;

      const isCorrect = state.handleAnswer(
        value,
        state.currentQuestion,
        currentQuizQuestion.id,
        correctAnswer,
        currentQuizQuestion.explanation,
        timeTaken,
        originalIndex
      );

      // Always show explanation after answering
      state.setShowExplanation(true);
    };

    const handleNavigateToQuestion = (index) => {
      console.log('Navigating to question:', {
        fromQuestion: state.currentQuestion,
        toQuestion: index,
        currentAnswers: state.answers,
        hasAnswer: state.answers[index] !== null
      });
      state.handleNavigate(index);
      // Show explanation only if the question has been answered
      if (state.answers[index] !== null) {
        state.setShowExplanation(true);
      } else {
        state.setShowExplanation(false);
      }
      state.startNewQuestion();
    };

    const handleNextQuestion = () => {
      handleNavigateToQuestion(state.currentQuestion + 1);
    };

    const handlePreviousQuestion = () => {
      handleNavigateToQuestion(state.currentQuestion - 1);
    };

    const handleRestart = () => {
      state.resetNavigation();
      state.resetAnswers();
      state.resetTiming();
      state.reshuffleQuiz();
    };

    return {
      handleAnswer: handleAnswerSubmit,
      handleNavigate: handleNavigateToQuestion,
      handleNext: handleNextQuestion,
      handlePrevious: handlePreviousQuestion,
      handleRestart
    };
  }, [state]);
}
