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

    // Ensure keywords exist and are valid
    if (!Array.isArray(quizData.keywords)) {
      quizData.keywords = [];
    }
    
    // Filter out invalid keywords and limit to 5
    quizData.keywords = quizData.keywords
      .filter(keyword => typeof keyword === 'string' && keyword.trim())
      .map(keyword => keyword.trim())
      .slice(0, 5);

    // If no keywords provided, extract from title
    if (quizData.keywords.length === 0) {
      const words = quizData.title.split(/\s+/)
        .filter(word => word.length > 3)  // Only words longer than 3 chars
        .slice(0, 3);  // Take up to 3 words
      quizData.keywords = words;
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
