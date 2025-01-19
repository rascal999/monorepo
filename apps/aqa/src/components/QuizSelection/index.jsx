import React, { useEffect, useState, useRef } from 'react';
import { getQuizzes, generateQuiz, generateQuizFromFile, deleteQuiz } from '../../api/client';
import GeneratingQuizView from '../GeneratingQuizView';
import SearchBar from './SearchBar';
import QuizList from './QuizList';
import styles from './QuizSelection.module.css';

const QuizSelection = ({ onSelectQuiz }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [generating, setGenerating] = useState(false);
  const fileInputRef = useRef(null);

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

  const handleDeleteQuiz = async (quizId) => {
    try {
      await deleteQuiz(quizId);
      setQuizzes(quizzes.filter(quiz => quiz.id !== quizId));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        setGenerating(true);
        const { id } = await generateQuizFromFile(file);
        const data = await getQuizzes();
        setQuizzes(data);
        onSelectQuiz(id);
      } catch (err) {
        setError(err.message);
      } finally {
        setGenerating(false);
        fileInputRef.current.value = '';
      }
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Loading quizzes...</h1>
      </div>
    );
  }

  if (generating) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Select a Quiz</h1>
        <GeneratingQuizView topic={searchTerm} />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Error</h1>
        <p className={styles.error}>{error}</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Select a Quiz</h1>
      <SearchBar
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        handleSearch={handleSearch}
        fileInputRef={fileInputRef}
        handleFileUpload={handleFileUpload}
        generating={generating}
      />
      <QuizList
        quizzes={quizzes}
        searchTerm={searchTerm}
        onSelectQuiz={onSelectQuiz}
        onDeleteQuiz={handleDeleteQuiz}
        generating={generating}
      />
    </div>
  );
};

export default QuizSelection;
