import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let db;

export const initDb = async () => {
  db = await open({
    filename: path.join(__dirname, 'quiz.db'),
    driver: sqlite3.Database
  });

  // Drop existing tables
  await db.exec(`
    DROP TABLE IF EXISTS user_answers;
    DROP TABLE IF EXISTS answers;
    DROP TABLE IF EXISTS questions;
    DROP TABLE IF EXISTS quizzes;
  `);

  // Create tables with new schema
  await db.exec(`
    CREATE TABLE quizzes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      keywords TEXT DEFAULT '[]',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE questions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      quiz_id INTEGER NOT NULL,
      question_text TEXT NOT NULL,
      explanation TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    );

    CREATE TABLE answers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      question_id INTEGER NOT NULL,
      answer_text TEXT NOT NULL,
      is_correct BOOLEAN NOT NULL DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );

    CREATE TABLE user_answers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      question_id INTEGER NOT NULL,
      answer_text TEXT NOT NULL,
      time_taken INTEGER NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );
  `);

  return db;
};

export const getQuizzes = async () => {
  const quizzes = await db.all('SELECT * FROM quizzes ORDER BY created_at DESC');
  return quizzes.map(quiz => ({
    ...quiz,
    keywords: quiz.keywords ? JSON.parse(quiz.keywords) : []
  }));
};

export const getQuizById = async (quizId) => {
  // Get quiz details
  const quiz = await db.get('SELECT * FROM quizzes WHERE id = ?', [quizId]);
  if (!quiz) {
    return null;
  }

  // Parse keywords with fallback to empty array
  quiz.keywords = quiz.keywords ? JSON.parse(quiz.keywords) : [];

  // Get questions with answers
  const questions = await db.all(
    'SELECT * FROM questions WHERE quiz_id = ? ORDER BY id',
    [quizId]
  );

  // Get answers for each question
  for (const question of questions) {
    question.answers = await db.all(
      'SELECT * FROM answers WHERE question_id = ? ORDER BY id',
      [question.id]
    );
  }

  return {
    ...quiz,
    questions,
  };
};

export const deleteQuiz = async (quizId) => {
  await db.run('BEGIN TRANSACTION');
  try {
    await db.run('DELETE FROM quizzes WHERE id = ?', [quizId]);
    await db.run('COMMIT');
    return true;
  } catch (error) {
    await db.run('ROLLBACK');
    throw error;
  }
};

export const createQuiz = async (title, questions, keywords = []) => {
  await db.run('BEGIN TRANSACTION');

  try {
    // Create quiz
    const quizResult = await db.run(
      'INSERT INTO quizzes (title, keywords) VALUES (?, ?)',
      [title, JSON.stringify(keywords)]
    );
    const quizId = quizResult.lastID;

    // Create questions and answers
    for (const q of questions) {
      const questionResult = await db.run(
        'INSERT INTO questions (quiz_id, question_text, explanation) VALUES (?, ?, ?)',
        [quizId, q.question_text, q.explanation]
      );
      const questionId = questionResult.lastID;

      for (const a of q.answers) {
        await db.run(
          'INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)',
          [questionId, a.answer_text, a.is_correct ? 1 : 0]
        );
      }
    }

    await db.run('COMMIT');
    return quizId;
  } catch (error) {
    await db.run('ROLLBACK');
    throw error;
  }
};
