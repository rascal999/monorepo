import fetch from 'node-fetch';
import { API_CONFIG, NETWORK_CONFIG } from './config.js';
import { httpsAgent, sleep, calculateBackoff, resolveHostname, logNetworkInfo } from './network.js';

// Hardcoded IPs for OpenRouter API as fallback
const FALLBACK_IPS = [
  '104.21.20.184',  // OpenRouter API IP
  '172.67.144.25'   // OpenRouter API alternate IP
];

/**
 * Makes a request to the OpenRouter API with retry logic
 * @param {Object} options - Request options
 * @returns {Promise<Object>} The API response data
 * @throws {Error} If all retry attempts fail
 */
async function makeRequest(options) {
  let lastError;
  let responseText;
  let urls = [API_CONFIG.url];

  // Log network status
  logNetworkInfo();

  // Try to resolve hostname
  try {
    const hostname = new URL(API_CONFIG.url).hostname;
    await resolveHostname(hostname);
  } catch (error) {
    console.log('DNS resolution failed, falling back to direct IP access');
    // Add fallback URLs using direct IPs
    urls = FALLBACK_IPS.map(ip => `https://${ip}/api/v1/chat/completions`);
    // Add Host header when using direct IP
    options.headers['Host'] = 'api.openrouter.ai';
  }

  for (let attempt = 1; attempt <= NETWORK_CONFIG.retryAttempts; attempt++) {
    // Try each URL in sequence
    for (const url of urls) {
      try {
        console.log(`API request attempt ${attempt}/${NETWORK_CONFIG.retryAttempts} using ${url}`);
        
        const response = await fetch(url, options);
        responseText = await response.text();

        if (response.ok) {
          return JSON.parse(responseText);
        }

        lastError = JSON.parse(responseText);
      } catch (error) {
        lastError = error;
        console.error('Request failed:', {
          attempt,
          url,
          error: {
            name: error.name,
            message: error.message,
            code: error.code
          }
        });
      }
    }

    if (attempt < NETWORK_CONFIG.retryAttempts) {
      const delay = calculateBackoff(attempt);
      console.log(`Retrying in ${delay}ms...`);
      await sleep(delay);
    }
  }

  throw new Error(`OpenRouter API error: ${lastError?.message || 'Request failed'}`);
}

/**
 * Makes a request to the OpenRouter API
 * @param {string} prompt - The prompt to send to the API
 * @returns {Promise<Object>} The API response data
 */
export async function callOpenRouter(prompt) {
  if (!process.env.OPENROUTER_API_KEY) {
    throw new Error('OPENROUTER_API_KEY environment variable is not set');
  }

  const options = {
    method: 'POST',
    agent: httpsAgent,
    headers: {
      ...API_CONFIG.headers,
      'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`
    },
    body: JSON.stringify({
      model: API_CONFIG.model,
      messages: [{ role: 'user', content: prompt }],
      temperature: API_CONFIG.temperature,
      max_tokens: API_CONFIG.maxTokens
    })
  };

  return makeRequest(options);
}

/**
 * Extracts the generated content from an OpenRouter API response
 * @param {Object} response - The API response
 * @returns {Object} The parsed content
 * @throws {Error} If the response format is invalid
 */
export function extractContent(response) {
  if (!response.choices?.[0]?.message?.content) {
    throw new Error('Invalid API response format: missing content');
  }

  try {
    const content = response.choices[0].message.content;
    console.log('Raw API response content:', content);
    
    // Try to clean the content before parsing
    const cleanedContent = content.trim();
    
    try {
      return JSON.parse(cleanedContent);
    } catch (firstError) {
      // Log the error and content for debugging
      console.error('JSON parse error:', firstError);
      console.error('Content that failed to parse:', cleanedContent);
      
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
