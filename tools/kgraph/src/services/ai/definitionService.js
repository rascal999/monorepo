import { fetchChatCompletion } from '../openRouterApi';
import { aiSettingsService } from './settingsService';
import { requestService } from './requestService';

class DefinitionService {
  constructor() {
    this.systemPrompt = `Define {term} in the context of {context}. Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. No parentheses around terms. Total response must be under 120 words.`;
  }

  async getDefinitions(terms, context = '') {
    console.log('DefinitionService: Fetching definitions for:', { terms, context });
    
    // Create messages for each term
    const requests = terms.map(term => ({
      messages: [
        { 
          role: 'system', 
          content: this.systemPrompt.replace('{term}', term).replace('{context}', context)
        },
        {
          role: 'user',
          content: `Define and explain: ${term}`
        }
      ]
    }));

    try {
      // Process requests in sequence but as a batch
      const responses = [];
      for (const request of requests) {
        const response = await fetchChatCompletion(
          request.messages, 
          aiSettingsService.getModel()
        );
        responses.push(response);
      }

      console.log('DefinitionService: Definitions received:', responses.length);
      return responses.map(response => ({
        success: true,
        message: response
      }));
    } catch (error) {
      console.error('DefinitionService: Error fetching definitions:', error);
      return requests.map(() => ({
        success: false,
        error: error.message || 'Failed to fetch definition'
      }));
    }
  }

  queueDefinitionRequest(term, context, callback) {
    // Generate unique request ID using term and context
    const requestId = `${term}-${context}`;
    
    requestService.queueRequest(
      requestId,
      callback,
      async () => {
        const results = await this.getDefinitions([term], context);
        if (results && results[0]) {
          return results[0];
        }
        throw new Error('No definition result received');
      }
    );
  }
}

export const definitionService = new DefinitionService();
