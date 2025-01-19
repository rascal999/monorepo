import fetch from 'node-fetch';
import { API_CONFIG, NETWORK_CONFIG } from '../config/config.js';
import { httpsAgent, sleep, calculateBackoff, resolveHostname, logNetworkInfo } from '../network/network.js';

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
export async function makeRequest(options) {
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

        console.log('Raw API response:', responseText);

        try {
          const parsedResponse = JSON.parse(responseText);
          console.log('Parsed API response:', JSON.stringify(parsedResponse, null, 2));

          if (response.ok) {
            if (!parsedResponse.choices?.[0]?.message?.content) {
              throw new Error('Invalid response structure: missing content');
            }
            return parsedResponse;
          }

          lastError = parsedResponse;
        } catch (parseError) {
          console.error('Failed to parse API response:', parseError);
          throw new Error(`Failed to parse API response: ${parseError.message}`);
        }
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
 * Creates request options for the OpenRouter API
 * @param {string} prompt - The prompt to send to the API
 * @returns {Object} The request options
 */
export function createRequestOptions(prompt) {
  if (!process.env.OPENROUTER_API_KEY) {
    throw new Error('OPENROUTER_API_KEY environment variable is not set');
  }

  return {
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
}
