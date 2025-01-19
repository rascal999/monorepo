import { QuizSchema } from './types.js';

/**
 * Validates quiz data against the schema
 * @param {Object} data - The quiz data to validate
 * @returns {Object} The validated quiz data
 * @throws {Error} If validation fails
 */
export function validateQuizData(data) {
  if (!matchesQuizSchema(data)) {
    throw new Error('Invalid quiz data structure');
  }
  return data;
}

/**
 * Checks if data matches the quiz schema
 * @param {Object} data - The data to check
 * @returns {boolean} True if data matches schema
 */
export function matchesQuizSchema(data) {
  try {
    if (!data || typeof data !== 'object') {
      return false;
    }

    if (!data.title || typeof data.title !== 'string') {
      return false;
    }

    if (!Array.isArray(data.questions) || data.questions.length === 0) {
      return false;
    }

    return data.questions.every(question => (
      question &&
      typeof question === 'object' &&
      typeof question.question_text === 'string' &&
      typeof question.explanation === 'string' &&
      Array.isArray(question.answers) &&
      question.answers.length === 4 &&
      question.answers.every(answer => (
        answer &&
        typeof answer === 'object' &&
        typeof answer.answer_text === 'string' &&
        typeof answer.is_correct === 'boolean'
      )) &&
      question.answers.filter(answer => answer.is_correct).length === 1
    ));
  } catch (error) {
    console.error('Schema validation error:', error);
    return false;
  }
}
