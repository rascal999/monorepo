import { useState, useCallback } from 'react';

export function useQuizState() {
  const [section, setSection] = useState('upload');
  const [title, setTitle] = useState('');
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [showAnswers, setShowAnswers] = useState(false);
  const [revealedQuestions, setRevealedQuestions] = useState(new Set());
  const [questionStartTime, setQuestionStartTime] = useState(0);
  const [questionTimes, setQuestionTimes] = useState([]);
  const [currentFileId, setCurrentFileId] = useState(null);
  const [flaggedQuestions, setFlaggedQuestions] = useState(new Set());
  const [showTimer, setShowTimer] = useState(true);
  const [showAnswersStraightaway, setShowAnswersStraightaway] = useState(false);
  const [hideAnswerFeedback, setHideAnswerFeedback] = useState(false);

  const calculateScore = useCallback((answers) => {
    return answers.reduce((total, answer, index) => {
      if (answer === undefined) return total;
      return total + (answer === questions[index]?.correctAnswer ? 1 : 0);
    }, 0);
  }, [questions]);

  const startQuiz = useCallback((quizData) => {
    try {
      setTitle(quizData.title);
      setQuestions(quizData.questions);
      setCurrentQuestionIndex(0);
      setScore(0);
      setUserAnswers([]);
      setElapsedTime(0);
      setSection('quiz');
      setShowTimer(quizData.preferences?.showTimer ?? true);
      setShowAnswersStraightaway(quizData.preferences?.showAnswersStraightaway ?? false);
      setHideAnswerFeedback(quizData.preferences?.hideAnswerFeedback ?? false);
      setIsTimerRunning(quizData.preferences?.showTimer ?? true);
      setShowAnswers(false);
      setRevealedQuestions(new Set());
      setQuestionTimes([]);
      setQuestionStartTime(Date.now());
      setCurrentFileId(quizData.fileId);
      setFlaggedQuestions(new Set());
    } catch (error) {
      console.error('Error starting quiz:', error);
      alert('Error starting quiz. Please try again.');
    }
  }, []);

  const handleOptionSelect = useCallback((selectedIndex) => {
    const currentQuestion = questions[currentQuestionIndex];
    if (!currentQuestion) return;

    // Only allow selection if no answer exists for current question
    if (userAnswers[currentQuestionIndex] === undefined) {
      setUserAnswers(prev => {
        const newAnswers = [...prev];
        newAnswers[currentQuestionIndex] = selectedIndex;
        const newScore = calculateScore(newAnswers);
        setScore(newScore);
        return newAnswers;
      });
    }
  }, [currentQuestionIndex, questions, calculateScore, userAnswers]);

  const handleRevealAnswers = useCallback(() => {
    setRevealedQuestions(prev => new Set([...prev, currentQuestionIndex]));
  }, [currentQuestionIndex]);

  const recordQuestionTime = useCallback(() => {
    const timeTaken = Date.now() - questionStartTime;
    setQuestionTimes(prev => [...prev, timeTaken]);
    setQuestionStartTime(Date.now());
  }, [questionStartTime]);

  const handleNextQuestion = useCallback(() => {
    if (currentQuestionIndex < questions.length - 1) {
      recordQuestionTime();
      setCurrentQuestionIndex(prev => prev + 1);
    }
  }, [currentQuestionIndex, questions.length, recordQuestionTime]);

  const handlePreviousQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      recordQuestionTime();
      setCurrentQuestionIndex(prev => prev - 1);
    }
  }, [currentQuestionIndex, recordQuestionTime]);

  const handleJumpToQuestion = useCallback((index) => {
    if (index >= 0 && index < questions.length) {
      recordQuestionTime();
      setCurrentQuestionIndex(index);
    }
  }, [questions.length, recordQuestionTime]);

  const finishQuiz = useCallback(() => {
    try {
      // Record the time for the last question before finishing
      recordQuestionTime();
      
      const finalElapsedTime = elapsedTime;
      setIsTimerRunning(false);
      setSection('results');
      setElapsedTime(finalElapsedTime);
      
      const finalScore = calculateScore(userAnswers);
      setScore(finalScore);
      
      if (currentFileId && window.updateQuizStats) {
        window.updateQuizStats(currentFileId, finalScore, finalElapsedTime);
      }
    } catch (error) {
      console.error('Error finishing quiz:', error);
    }
  }, [currentFileId, elapsedTime, calculateScore, userAnswers, recordQuestionTime]);

  const handleTimerTick = useCallback((time) => {
    setElapsedTime(time);
  }, []);

  const restartQuiz = useCallback(() => {
    try {
      setSection('upload');
      setTitle('');
      setIsTimerRunning(false);
      setElapsedTime(0);
      setShowAnswers(false);
      setRevealedQuestions(new Set());
      setQuestionTimes([]);
      setCurrentFileId(null);
      setFlaggedQuestions(new Set());
      setShowTimer(true);
      setShowAnswersStraightaway(false);
      setHideAnswerFeedback(false);
    } catch (error) {
      console.error('Error restarting quiz:', error);
    }
  }, []);

  const toggleQuestionFlag = useCallback((index) => {
    setFlaggedQuestions(prev => {
      const newFlags = new Set(prev);
      if (newFlags.has(index)) {
        newFlags.delete(index);
      } else {
        newFlags.add(index);
      }
      return newFlags;
    });
  }, []);

  return {
    // State
    section,
    title,
    questions,
    currentQuestionIndex,
    score,
    userAnswers,
    elapsedTime,
    isTimerRunning,
    showAnswers,
    revealedQuestions,
    questionTimes,
    currentFileId,
    flaggedQuestions,
    showTimer,
    showAnswersStraightaway,
    hideAnswerFeedback,

    // Actions
    startQuiz,
    handleOptionSelect,
    handleRevealAnswers,
    handleNextQuestion,
    handlePreviousQuestion,
    handleJumpToQuestion,
    finishQuiz,
    handleTimerTick,
    restartQuiz,
    toggleQuestionFlag,
    setShowAnswers
  };
}
