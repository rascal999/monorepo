import { makeRequest, createRequestOptions } from './request.js';
import { extractContent, validateQuizFormat } from './response-parser.js';

/**
 * Makes a request to the OpenRouter API
 * @param {string} prompt - The prompt to send to the API
 * @returns {Promise<Object>} The API response data
 */
export async function callOpenRouter(prompt) {
  try {
    console.log('Making OpenRouter API request...');
    const options = createRequestOptions(prompt);
    const response = await makeRequest(options);
    
    console.log('Extracting content from response...');
    const content = extractContent(response);
    
    console.log('Validating quiz format...');
    if (!validateQuizFormat(content)) {
      throw new Error('Generated content does not match expected quiz format');
    }
    
    return content;
  } catch (error) {
    console.error('OpenRouter API call failed:', {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    });
    throw error;
  }
}

// Re-export necessary functions
export { extractContent } from './response-parser.js';
