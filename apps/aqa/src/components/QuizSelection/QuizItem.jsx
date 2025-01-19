import React from 'react';
import styles from './QuizItem.module.css';
import { deleteQuiz } from '../../api/client';

const QuizItem = ({ quiz, onSelect, onDelete }) => {
  const handleDelete = async (e) => {
    e.stopPropagation();
    try {
      await deleteQuiz(quiz.id);
      onDelete(quiz.id);
    } catch (error) {
      console.error('Failed to delete quiz:', error);
    }
  };

  return (
    <div
      className={styles.container}
      onClick={() => onSelect(quiz.id)}
    >
      <div className={styles.header}>
        <h2 className={styles.title}>{quiz.title}</h2>
        <button 
          className={styles.deleteButton}
          onClick={handleDelete}
          title="Delete quiz"
        >
          <svg className={styles.deleteIcon} viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
      </div>
      {quiz.keywords && quiz.keywords.length > 0 && (
        <div className={styles.keywords}>
          {quiz.keywords.map((keyword, index) => (
            <span key={index} className={styles.keyword}>
              {keyword}
            </span>
          ))}
        </div>
      )}
      <span className={styles.createdAt}>
        Created: {new Date(quiz.created_at).toLocaleDateString()}
      </span>
    </div>
  );
};

export default QuizItem;
