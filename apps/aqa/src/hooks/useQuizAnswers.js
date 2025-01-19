import { useState, useEffect } from 'react';

export function useQuizAnswers(totalQuestions) {
  // Initialize state arrays with proper length
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState(() => new Array(totalQuestions).fill(null));
  const [answerStatuses, setAnswerStatuses] = useState(() => new Array(totalQuestions).fill(null));
  const [userAnswers, setUserAnswers] = useState(() => new Array(totalQuestions).fill(null));

  // Re-initialize arrays if totalQuestions changes
  useEffect(() => {
    console.log('Reinitializing answer arrays with length:', totalQuestions);
    if (answers.length !== totalQuestions) {
      setAnswers(new Array(totalQuestions).fill(null));
      setAnswerStatuses(new Array(totalQuestions).fill(null));
      setUserAnswers(new Array(totalQuestions).fill(null));
    }
  }, [totalQuestions, answers.length]);

  const handleAnswer = (
    value,
    currentQuestion,
    questionId,
    correctAnswer,
    explanation,
    timeTaken,
    originalQuestionIndex
  ) => {
    console.log('handleAnswer called with:', {
      value,
      currentQuestion,
      questionId,
      correctAnswerText: correctAnswer.answer_text,
      totalQuestions,
      currentAnswersLength: answers.length,
      currentAnswers: answers
    });

    const isCorrect = value === correctAnswer.answer_text;
    
    if (isCorrect) {
      setScore(prevScore => prevScore + 1);
    }
    
    // Update only the current question's answer
    setAnswers(prevAnswers => {
      // Create a new array with the same length
      const newAnswers = Array(totalQuestions).fill(null);
      // Copy over all previous answers
      for (let i = 0; i < prevAnswers.length; i++) {
        newAnswers[i] = prevAnswers[i];
      }
      // Set the new answer
      newAnswers[currentQuestion] = value;
      
      console.log('Answer update:', {
        currentQuestion,
        value,
        prevAnswers,
        newAnswers
      });
      
      return newAnswers;
    });

    setAnswerStatuses(prevStatuses => {
      // Ensure we have the correct array length
      const newStatuses = prevStatuses.length === totalQuestions 
        ? [...prevStatuses]
        : new Array(totalQuestions).fill(null);
      newStatuses[currentQuestion] = isCorrect ? 'correct' : 'incorrect';
      return newStatuses;
    });

    setUserAnswers(prevUserAnswers => {
      // Ensure we have the correct array length
      const newUserAnswers = prevUserAnswers.length === totalQuestions 
        ? [...prevUserAnswers]
        : new Array(totalQuestions).fill(null);
      newUserAnswers[currentQuestion] = {
        questionId,
        answerText: value,
        timeTaken,
        isCorrect,
        correctAnswer: correctAnswer.answer_text,
        explanation,
        originalQuestionIndex
      };
      return newUserAnswers;
    });

    return isCorrect;
  };

  const resetAnswers = () => {
    console.log('Resetting answers with length:', totalQuestions);
    setScore(0);
    setAnswers(new Array(totalQuestions).fill(null));
    setAnswerStatuses(new Array(totalQuestions).fill(null));
    setUserAnswers(new Array(totalQuestions).fill(null));
  };

  return {
    score,
    answers,
    answerStatuses,
    userAnswers,
    handleAnswer,
    resetAnswers
  };
}
