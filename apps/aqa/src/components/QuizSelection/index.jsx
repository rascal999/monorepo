import React, { useEffect, useState } from 'react';
import { getQuizzes } from '../../api/client';
import './styles.css';

const QuizSelection = ({ onSelectQuiz }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        const data = await getQuizzes();
        setQuizzes(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load quizzes. Please try again later.');
        setLoading(false);
      }
    };

    fetchQuizzes();
  }, []);

  if (loading) {
    return (
      <div className="quiz-selection">
        <h1>Loading quizzes...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="quiz-selection">
        <h1>Error</h1>
        <p className="error-message">{error}</p>
      </div>
    );
  }

  return (
    <div className="quiz-selection">
      <h1>Select a Quiz</h1>
      <div className="quiz-list">
        {quizzes.length === 0 ? (
          <p>No quizzes available.</p>
        ) : (
          quizzes.map((quiz) => (
            <button
              key={quiz.id}
              className="quiz-item"
              onClick={() => onSelectQuiz(quiz.id)}
            >
              <h2>{quiz.title}</h2>
              <span className="created-at">
                Created: {new Date(quiz.created_at).toLocaleDateString()}
              </span>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default QuizSelection;
