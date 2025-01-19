/**
 * Generates the prompt for quiz creation
 * @param {string|null} topic - The topic to create a quiz about
 * @param {string|null} content - The content to base the quiz on
 * @returns {string} The formatted prompt
 */
export function generatePrompt(topic, content = null) {
  const basePrompt = content
    ? `Generate a quiz based on this content with 5 multiple choice questions. Each question should have 4 options (one correct) and a brief explanation. Generate an appropriate title.

Content: ${content}`
    : `Create a quiz about "${topic}" with 5 multiple choice questions. Each question should have 4 options (one correct) and a brief explanation.`;

  return `${basePrompt}

Also generate 3-5 relevant keywords that describe the main topics or concepts covered in the quiz.

Return JSON with this structure (no extra text):
{
  "title": "string",
  "keywords": ["string"],
  "questions": [{
    "question_text": "string",
    "explanation": "string",
    "answers": [
      {"answer_text": "string", "is_correct": boolean}
    ]
  }]
}

Rules: 4 answers per question, one correct answer, no comments/placeholders.`;
}
