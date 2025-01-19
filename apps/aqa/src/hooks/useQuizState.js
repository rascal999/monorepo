import { useQuizData } from './useQuizData';
import { useQuizNavigation } from './useQuizNavigation';
import { useQuizAnswers } from './useQuizAnswers';
import { useQuizTiming } from './useQuizTiming';

export function useQuizState(quizId) {
  const { quiz, loading, error, questionOrder, reshuffleQuiz } = useQuizData(quizId);
  // Initialize totalQuestions only after quiz is loaded
  const totalQuestions = quiz?.questions?.length || 0;
  console.log('useQuizState:', {
    totalQuestions,
    hasQuiz: !!quiz,
    questionsLength: quiz?.questions?.length
  });

  // Wait for quiz to load before initializing state
  const navigation = useQuizNavigation(totalQuestions);
  const answerState = useQuizAnswers(totalQuestions);
  const timing = useQuizTiming(totalQuestions);

  // Log state initialization
  console.log('useQuizState initialized:', {
    navigation: {
      currentQuestion: navigation.currentQuestion,
      showExplanation: navigation.showExplanation
    },
    answers: {
      length: answerState.answers.length,
      values: answerState.answers
    },
    timing: {
      answerTimes: timing.answerTimes
    }
  });

  const state = {
    // Quiz data
    quiz,
    loading,
    error,
    questionOrder,
    totalQuestions,
    currentQuestion: navigation.currentQuestion,
    question: quiz?.questions?.[navigation.currentQuestion],

    // Navigation state
    showExplanation: navigation.showExplanation,
    completed: navigation.completed,
    markedQuestions: navigation.markedQuestions,
    isMarked: navigation.markedQuestions[navigation.currentQuestion],

    // Answer state
    score: answerState.score,
    answers: answerState.answers,
    answerStatuses: answerState.answerStatuses,
    userAnswers: answerState.userAnswers,

    // Timing state
    answerTimes: timing.answerTimes,
    averageAnswerTime: timing.getAverageAnswerTime(),

    // Actions
    setShowExplanation: navigation.setShowExplanation,
    setCompleted: navigation.setCompleted,
    handleNext: navigation.handleNext,
    handlePrevious: navigation.handlePrevious,
    handleNavigate: navigation.handleNavigate,
    handleAnswer: answerState.handleAnswer,
    toggleMarkQuestion: navigation.toggleMarkQuestion,
    resetNavigation: navigation.resetNavigation,
    resetAnswers: answerState.resetAnswers,
    resetTiming: timing.resetTiming,
    reshuffleQuiz,
    recordAnswerTime: timing.recordAnswerTime,
    startNewQuestion: timing.startNewQuestion
  };

  if (loading) {
    return { loading: true };
  }

  if (error) {
    return { error };
  }

  if (!quiz) {
    return { error: 'Quiz not found' };
  }

  return state;
}
