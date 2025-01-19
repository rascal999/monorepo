/**
 * @typedef {Object} Answer
 * @property {string} answer_text - The text of the answer option
 * @property {boolean} is_correct - Whether this is the correct answer
 */

/**
 * @typedef {Object} Question
 * @property {string} question_text - The text of the question
 * @property {string} explanation - Explanation for the correct answer
 * @property {Answer[]} answers - Array of answer options
 */

/**
 * @typedef {Object} Quiz
 * @property {string} title - The title of the quiz
 * @property {string[]} [keywords] - Array of keywords describing the quiz content
 * @property {Question[]} questions - Array of quiz questions
 */

export const QuizSchema = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    keywords: {
      type: 'array',
      items: { type: 'string' },
      minItems: 0,
      maxItems: 5
    },
    questions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          question_text: { type: 'string' },
          explanation: { type: 'string' },
          answers: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                answer_text: { type: 'string' },
                is_correct: { type: 'boolean' }
              },
              required: ['answer_text', 'is_correct']
            },
            minItems: 4,
            maxItems: 4
          }
        },
        required: ['question_text', 'explanation', 'answers']
      },
      minItems: 1
    }
  },
  required: ['title', 'questions']
};
