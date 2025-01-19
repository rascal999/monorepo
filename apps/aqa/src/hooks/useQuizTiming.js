import { useState } from 'react';

export function useQuizTiming(totalQuestions) {
  const [answerTimes, setAnswerTimes] = useState(Array(totalQuestions).fill(null));
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());

  const recordAnswerTime = (currentQuestion) => {
    const timeTaken = Date.now() - questionStartTime;
    const newAnswerTimes = [...answerTimes];
    newAnswerTimes[currentQuestion] = timeTaken;
    setAnswerTimes(newAnswerTimes);
    return timeTaken;
  };

  const startNewQuestion = () => {
    setQuestionStartTime(Date.now());
  };

  const resetTiming = () => {
    setAnswerTimes(Array(totalQuestions).fill(null));
    setQuestionStartTime(Date.now());
  };

  const getAverageAnswerTime = () => {
    const validTimes = answerTimes.filter(time => time !== null);
    if (validTimes.length === 0) return 0;
    return validTimes.reduce((a, b) => a + b, 0) / validTimes.length;
  };

  return {
    answerTimes,
    recordAnswerTime,
    startNewQuestion,
    resetTiming,
    getAverageAnswerTime
  };
}
