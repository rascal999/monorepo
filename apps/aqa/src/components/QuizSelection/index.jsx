import React, { useEffect, useState } from 'react';
import { getQuizzes, generateQuiz } from '../../api/client';
import GeneratingQuizView from '../GeneratingQuizView';
import './styles.css';

const QuizSelection = ({ onSelectQuiz }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [generating, setGenerating] = useState(false);

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

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    const matchingQuizzes = quizzes.filter(quiz =>
      quiz.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (matchingQuizzes.length === 0) {
      try {
        setGenerating(true);
        const { id } = await generateQuiz(searchTerm);
        const data = await getQuizzes();
        setQuizzes(data);
        onSelectQuiz(id);
      } catch (err) {
        setError(err.message);
      } finally {
        setGenerating(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="quiz-selection">
        <h1>Loading quizzes...</h1>
      </div>
    );
  }

  if (generating) {
    return (
      <div className="quiz-selection">
        <h1>Select a Quiz</h1>
        <GeneratingQuizView topic={searchTerm} />
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

  const filteredQuizzes = quizzes.filter(quiz =>
    quiz.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="quiz-selection">
      <h1>Select a Quiz</h1>
      <div className="search-container">
        <input
          type="text"
          placeholder="Search or enter a topic for a new quiz..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="search-input"
          disabled={generating}
        />
        <button 
          onClick={handleSearch}
          className="search-button"
          disabled={generating || !searchTerm.trim()}
        >
          {generating ? 'Generating Quiz...' : 'Search'}
        </button>
      </div>
      <div className="quiz-list">
        {filteredQuizzes.length === 0 ? (
          <div className="no-results">
            <p>No quizzes found.</p>
            {!generating && searchTerm.trim() && (
              <p className="generate-hint">
                Press Enter or click Search to generate a new quiz about "{searchTerm}"
              </p>
            )}
          </div>
        ) : (
          filteredQuizzes.map((quiz) => (
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
