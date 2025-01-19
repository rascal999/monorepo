import { useState, useEffect } from 'react';
import { getQuizById } from '../api/client';
import { shuffle } from '../utils/shuffle';

export function useQuizData(quizId) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [questionOrder, setQuestionOrder] = useState([]);

  const shuffleQuiz = (data) => {
    console.log('Original quiz data:', {
      totalQuestions: data.questions.length,
      questionIds: data.questions.map(q => q.id)
    });

    // Add original indices to questions before shuffling
    const questionsWithIndices = data.questions.map((question, index) => ({
      ...question,
      originalIndex: index
    }));

    // Shuffle questions and store the order
    const shuffledQuestions = shuffle(questionsWithIndices);
    const order = shuffledQuestions.map(q => q.id);
    setQuestionOrder(order);

    console.log('After shuffle:', {
      questionOrder: order,
      questionMapping: shuffledQuestions.map(q => ({
        id: q.id,
        originalIndex: q.originalIndex,
        currentIndex: shuffledQuestions.indexOf(q)
      }))
    });
    
    // Shuffle answers for each question
    const questionsWithShuffledAnswers = shuffledQuestions.map(question => ({
      ...question,
      answers: shuffle(question.answers)
    }));
    
    setQuiz({
      ...data,
      questions: questionsWithShuffledAnswers
    });
  };

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const data = await getQuizById(quizId);
        shuffleQuiz(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load quiz. Please try again later.');
        setLoading(false);
      }
    };

    if (quizId) {
      fetchQuiz();
    }
  }, [quizId]);

  const reshuffleQuiz = () => {
    if (quiz) {
      shuffleQuiz(quiz);
    }
  };

  return {
    quiz,
    loading,
    error,
    questionOrder,
    reshuffleQuiz
  };
}
