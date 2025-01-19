/**
 * Extracts the generated content from an OpenRouter API response
 * @param {Object} response - The API response
 * @returns {Object} The parsed content
 * @throws {Error} If the response format is invalid
 */
export function extractContent(response) {
  validateResponse(response);
  return parseContent(response);
}

/**
 * Validates the structure of an OpenRouter API response
 * @param {Object} response - The API response to validate
 * @throws {Error} If the response format is invalid
 */
function validateResponse(response) {
  console.log('Full API response:', JSON.stringify(response, null, 2));
  
  if (!response.choices) {
    throw new Error('Invalid API response format: missing choices array');
  }
  
  if (!response.choices[0]) {
    throw new Error('Invalid API response format: empty choices array');
  }
  
  if (!response.choices[0].message) {
    throw new Error('Invalid API response format: missing message object');
  }
  
  if (!response.choices[0].message.content) {
    throw new Error('Invalid API response format: missing content in message');
  }
}

/**
 * Parses the content from a validated API response
 * @param {Object} response - The validated API response
 * @returns {Object} The parsed content
 * @throws {Error} If parsing fails
 */
function parseContent(response) {
  try {
    console.log('Processing API response content...');
    const content = response.choices[0].message.content;
    console.log('Raw API response content:', content);
    console.log('Content type:', typeof content);
    console.log('Content length:', content.length);
    
    // Try to clean the content before parsing
    const cleanedContent = content.trim();
    
    try {
      return JSON.parse(cleanedContent);
    } catch (firstError) {
      // Log the error and content for debugging
      console.error('JSON parse error:', {
        error: firstError.message,
        contentType: typeof cleanedContent,
        contentLength: cleanedContent.length,
        content: cleanedContent
      });
      
      // Try to extract JSON if there's extra text
      const jsonMatch = cleanedContent.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const extractedJson = jsonMatch[0];
        console.log('Attempting to parse extracted JSON:', extractedJson);
        try {
          return JSON.parse(extractedJson);
        } catch (secondError) {
          console.error('Failed to parse extracted JSON:', secondError);
        }
      }
      
      throw new Error(`Failed to parse quiz data: ${firstError.message}`);
    }
  } catch (error) {
    console.error('Content extraction failed:', error);
    throw new Error(`Failed to parse quiz data: ${error.message}`);
  }
}

/**
 * Validates that the parsed content matches the expected quiz format
 * @param {Object} content - The parsed content to validate
 * @returns {boolean} True if the content is valid
 */
export function validateQuizFormat(content) {
  if (!content || typeof content !== 'object') {
    return false;
  }

  if (typeof content.title !== 'string' || !content.title.trim()) {
    return false;
  }

  if (!Array.isArray(content.questions) || content.questions.length === 0) {
    return false;
  }

  return content.questions.every(question => (
    typeof question.question_text === 'string' &&
    typeof question.explanation === 'string' &&
    Array.isArray(question.answers) &&
    question.answers.length === 4 &&
    question.answers.every(answer => (
      typeof answer.answer_text === 'string' &&
      typeof answer.is_correct === 'boolean'
    )) &&
    question.answers.filter(answer => answer.is_correct).length === 1
  ));
}
