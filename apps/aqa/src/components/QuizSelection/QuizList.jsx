import React from 'react';
import QuizItem from './QuizItem';
import styles from './QuizList.module.css';

const QuizList = ({ quizzes, searchTerm, onSelectQuiz, onDeleteQuiz, generating }) => {
  const filteredQuizzes = quizzes.filter(quiz => {
    const searchTermLower = searchTerm.toLowerCase();
    return (
      quiz.title.toLowerCase().includes(searchTermLower) ||
      (quiz.keywords && quiz.keywords.some(keyword => 
        keyword.toLowerCase().includes(searchTermLower)
      ))
    );
  });

  if (filteredQuizzes.length === 0) {
    return (
      <div className={styles.noResults}>
        <p>No quizzes found.</p>
        {!generating && searchTerm.trim() && (
          <p className={styles.generateHint}>
            Press Enter or click Search to generate a new quiz about "{searchTerm}"
          </p>
        )}
      </div>
    );
  }

  if (filteredQuizzes.length <= 2) {
    return (
      <div className={styles.singleResult}>
        {filteredQuizzes.map((quiz) => (
          <QuizItem
            key={quiz.id}
            quiz={quiz}
            onSelect={onSelectQuiz}
            onDelete={onDeleteQuiz}
          />
        ))}
      </div>
    );
  }

  return (
    <div className={styles.gridContainer}>
      {filteredQuizzes.map((quiz) => (
        <QuizItem
          key={quiz.id}
          quiz={quiz}
          onSelect={onSelectQuiz}
          onDelete={onDeleteQuiz}
        />
      ))}
    </div>
  );
};

export default QuizList;
