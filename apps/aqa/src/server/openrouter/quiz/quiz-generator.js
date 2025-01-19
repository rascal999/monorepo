import { callOpenRouter } from '../api/api.js';
import { validateQuizData, matchesQuizSchema } from '../validation/validation.js';
import { generatePrompt } from './prompt-generator.js';
import { fixQuizData } from './quiz-fixer.js';

/**
 * Generates a quiz about the given topic using AI
 * @param {string} topic - The topic to create a quiz about
 * @returns {Promise<import('../validation/types.js').Quiz>} The generated quiz data
 * @throws {Error} If quiz generation or validation fails
 */
export async function generateQuiz(topic) {
  return await generateQuizInternal(topic);
}

/**
 * Generates a quiz from provided content using AI
 * @param {string} content - The content to base the quiz on
 * @returns {Promise<import('../validation/types.js').Quiz>} The generated quiz data
 * @throws {Error} If quiz generation or validation fails
 */
export async function generateQuizFromContent(content) {
  return await generateQuizInternal(null, content);
}

/**
 * Internal function to generate a quiz using AI
 * @param {string|null} topic - The topic to create a quiz about
 * @param {string|null} content - The content to base the quiz on
 * @returns {Promise<import('../validation/types.js').Quiz>} The generated quiz data
 * @throws {Error} If quiz generation or validation fails
 */
async function generateQuizInternal(topic = null, content = null) {
  console.log('Starting quiz generation', topic ? `for topic: ${topic}` : 'from content');

  try {
    // Generate and validate the quiz
    const prompt = generatePrompt(topic, content);
    const response = await callOpenRouter(prompt);
    const quizData = response;

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
    const errorContext = topic ? `about "${topic}"` : 'from content';
    throw new Error(`Failed to generate quiz ${errorContext}: ${error.message}`);
  }
}
