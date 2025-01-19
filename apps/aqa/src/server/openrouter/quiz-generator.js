import { callOpenRouter, extractContent } from './api.js';
import { validateQuizData, matchesQuizSchema } from './validation.js';

/**
 * Generates the prompt for quiz creation
 * @param {string} topic - The topic to create a quiz about
 * @returns {string} The formatted prompt
 */
function generatePrompt(topic) {
  return `Create a quiz about "${topic}" with 5 multiple choice questions. Each question must have exactly 4 options with only one correct answer and include an explanation for the correct answer.

Return a valid JSON object with this exact structure (no comments or extra text):
{
  "title": "Quiz title here",
  "questions": [
    {
      "question_text": "Question text here",
      "explanation": "Explanation for the correct answer here",
      "answers": [
        {
          "answer_text": "First answer option",
          "is_correct": false
        },
        {
          "answer_text": "Second answer option",
          "is_correct": true
        },
        {
          "answer_text": "Third answer option",
          "is_correct": false
        },
        {
          "answer_text": "Fourth answer option",
          "is_correct": false
        }
      ]
    }
  ]
}

Requirements:
1. Response must be a single JSON object with no additional text
2. Each question must have exactly 4 answer options in an array
3. Exactly one answer per question must have "is_correct": true
4. All text fields must be non-empty strings
5. All is_correct fields must be boolean (true/false)
6. Do not include any comments or placeholders in the JSON`;
}

/**
 * Generates a quiz about the given topic using AI
 * @param {string} topic - The topic to create a quiz about
 * @returns {Promise<import('./types.js').Quiz>} The generated quiz data
 * @throws {Error} If quiz generation or validation fails
 */
export async function generateQuiz(topic) {
  console.log('Starting quiz generation for topic:', topic);

  try {
    // Generate and validate the quiz
    const prompt = generatePrompt(topic);
    const response = await callOpenRouter(prompt);
    const quizData = extractContent(response);

    // Pre-validation schema check
    if (!matchesQuizSchema(quizData)) {
      console.error('Generated quiz does not match schema:', JSON.stringify(quizData, null, 2));
      
      // Detailed validation logging
      const questions = quizData.questions || [];
      questions.forEach((q, i) => {
        if (!q.answers || !Array.isArray(q.answers)) {
          console.error(`Question ${i + 1} answers invalid:`, q.answers);
        } else {
          console.error(`Question ${i + 1} answers:`, JSON.stringify(q.answers, null, 2));
        }
      });
      
      // Try to fix common issues
      const fixedData = fixQuizData(quizData);
      if (matchesQuizSchema(fixedData)) {
        console.log('Successfully fixed quiz data');
        quizData = fixedData;
      } else {
        throw new Error('Generated quiz has invalid structure and could not be fixed');
      }
    }

    // Full validation
    const validatedQuiz = validateQuizData(quizData);
    console.log('Successfully generated and validated quiz:', {
      title: validatedQuiz.title,
      questionCount: validatedQuiz.questions.length
    });

    return validatedQuiz;
  } catch (error) {
    console.error('Quiz generation failed:', {
      topic,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    });
    throw new Error(`Failed to generate quiz about "${topic}": ${error.message}`);
  }
}

/**
 * Attempts to fix common issues in generated quiz data
 * @param {Object} quizData - The quiz data to fix
 * @returns {Object} The fixed quiz data
 */
export function fixQuizData(quizData) {
  try {
    // Ensure title exists and is a string
    if (!quizData.title || typeof quizData.title !== 'string') {
      quizData.title = 'Generated Quiz';
    }

    // Ensure questions array exists
    if (!Array.isArray(quizData.questions)) {
      throw new Error('Cannot fix quiz: questions must be an array');
    }

    // Fix each question
    quizData.questions = quizData.questions.map((question, index) => {
      // Fix missing or invalid question text
      if (!question.question_text || typeof question.question_text !== 'string') {
        question.question_text = `Question ${index + 1}`;
      }

      // Fix missing or invalid explanation
      if (!question.explanation || typeof question.explanation !== 'string') {
        question.explanation = 'No explanation provided';
      }

      // Fix answers array
      if (!Array.isArray(question.answers)) {
        question.answers = [];
      }

      // Ensure exactly 4 answers
      while (question.answers.length < 4) {
        question.answers.push({
          answer_text: `Option ${question.answers.length + 1}`,
          is_correct: false
        });
      }

      // Ensure at least one correct answer
      let hasCorrectAnswer = question.answers.some(answer => answer.is_correct);
      if (!hasCorrectAnswer) {
        question.answers[0].is_correct = true;
      }

      return question;
    });

    return quizData;
  } catch (error) {
    console.error('Failed to fix quiz data:', error);
    throw error;
  }
}
