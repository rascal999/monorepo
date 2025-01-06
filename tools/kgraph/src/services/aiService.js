import { fetchChatCompletion } from './openRouterApi';

class AIService {
  constructor() {
    this.batchQueue = new Map(); // Map of term -> array of callbacks
    this.batchTimeout = null;
    this.BATCH_DELAY = 250; // Reduced delay to improve responsiveness
    this.activeRequests = new Set(); // Track active requests to prevent duplicates

    // Load model settings
    const savedSettings = localStorage.getItem('modelSettings');
    if (savedSettings) {
      const { model, temperature } = JSON.parse(savedSettings);
      this.model = model;
      this.temperature = temperature;
    } else {
      this.model = 'openai/gpt-4-turbo';
      this.temperature = 0.7;
    }

    this.systemPrompt = `You are a knowledgeable assistant helping to define concepts and explain their relationships. When given a term or concept:
1. Provide a clear, concise definition
2. Explain key aspects and relationships
3. Use academic/technical language when appropriate
4. Keep responses focused and relevant
5. Aim for 2-3 paragraphs maximum`;
  }

  clearStaleRequests() {
    console.log('AIService: Clearing stale requests:', {
      activeRequests: [...this.activeRequests],
      queueSize: this.batchQueue.size
    });

    // Clear timeout first to prevent new requests
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    // Process any pending callbacks with cancellation
    Array.from(this.batchQueue.entries()).forEach(([requestId, request]) => {
      request.callbacks.forEach(({ callback }) => {
        callback({
          success: false,
          error: 'Request cancelled due to graph change'
        });
      });
    });

    // Clear tracking state
    this.activeRequests.clear();
    this.batchQueue = new Map();
  }

  async getDefinitions(terms, context = '') {
    console.log('AIService: Fetching definitions for:', { terms, context });
    
    // Create messages for each term
    const requests = terms.map(term => ({
      messages: [
        { 
          role: 'system', 
          content: `Define ${term} in the context of ${context}. Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. No parentheses around terms. Total response must be under 120 words.` 
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
        const response = await fetchChatCompletion(request.messages, this.model);
        responses.push(response);
      }

      console.log('AIService: Definitions received:', responses.length);
      return responses.map(response => ({
        success: true,
        message: response
      }));
    } catch (error) {
      console.error('AIService: Error fetching definitions:', error);
      return requests.map(() => ({
        success: false,
        error: error.message || 'Failed to fetch definition'
      }));
    }
  }

  // Queue a definition request for batch processing
  queueDefinitionRequest(term, context, callback) {
    // Generate unique request ID using term and context
    const requestId = `${term}-${context}`;
    
    // Skip if exact request is already being processed
    if (this.activeRequests.has(requestId)) {
      console.log('AIService: Request already in progress:', { term, context });
      return;
    }

    console.log('AIService: Queueing request:', {
      requestId,
      term,
      context,
      activeRequests: [...this.activeRequests],
      queueSize: this.batchQueue.size
    });

    // Add to queue with unique ID
    if (!this.batchQueue.has(requestId)) {
      this.batchQueue.set(requestId, { term, callbacks: [] });
    }
    this.batchQueue.get(requestId).callbacks.push({ context, callback });
    this.activeRequests.add(requestId);

    // Clear existing timeout
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }

    // Set new timeout to process batch
    this.batchTimeout = setTimeout(async () => {
      const currentBatch = new Map(this.batchQueue);
      this.batchQueue = new Map(); // Clear queue

      if (currentBatch.size > 0) {
        console.log('AIService: Processing batch of', currentBatch.size, 'requests');
        const requests = Array.from(currentBatch.values());
        const terms = requests.map(r => r.term);
        const context = requests[0].callbacks[0].context; // Use context from first request
        
        try {
          const results = await this.getDefinitions(terms, context);
          
          // Process results
          Array.from(currentBatch.entries()).forEach(([requestId, request], index) => {
            const result = results[index];
            
            // Call all callbacks for this request
            request.callbacks.forEach(({ callback }) => {
              callback(result);
            });
            
            this.activeRequests.delete(requestId);
          });
        } catch (error) {
          console.error('AIService: Batch processing error:', error);
          // Handle error for all requests in batch
          Array.from(currentBatch.entries()).forEach(([requestId, request]) => {
            request.callbacks.forEach(({ callback }) => {
              callback({
                success: false,
                error: error.message || 'Failed to fetch definition'
              });
            });
            this.activeRequests.delete(requestId);
          });
        }
      }
    }, this.BATCH_DELAY);
  }

  async getChatResponse(messages, context = '') {
    console.log('AIService: Getting chat response:', { context, messageCount: messages.length });
    
    const fullMessages = [
      { 
        role: 'system', 
        content: `${this.systemPrompt}\nContext: ${context}`
      },
      ...messages
    ];

    try {
      const response = await fetchChatCompletion(fullMessages, this.model);
      console.log('AIService: Chat response received');
      return {
        success: true,
        message: response
      };
    } catch (error) {
      console.error('AIService: Error getting chat response:', error);
      return {
        success: false,
        error: error.message || 'Failed to get response'
      };
    }
  }

  async searchSources(keyword) {
    console.log('AIService: Searching sources for:', keyword);
    
    const messages = [
      {
        role: 'system',
        content: 'Search the web for recent and reliable sources on the given topic. Return a list of URLs with titles and brief descriptions. Focus on academic, scientific, or reputable sources. Format response as JSON array with objects containing url, title, and description fields.'
      },
      {
        role: 'user',
        content: `Search for sources about: ${keyword}`
      }
    ];

    try {
      const response = await fetchChatCompletion(messages, this.model);
      console.log('AIService: Sources received');
      
      let sources;
      try {
        sources = JSON.parse(response.content);
      } catch (err) {
        console.error('Failed to parse sources JSON:', err);
        throw new Error('Invalid response format from AI');
      }

      return {
        success: true,
        sources
      };
    } catch (error) {
      console.error('AIService: Error searching sources:', error);
      return {
        success: false,
        error: error.message || 'Failed to search sources'
      };
    }
  }

  updateSettings() {
    const savedSettings = localStorage.getItem('modelSettings');
    if (savedSettings) {
      const { model, temperature } = JSON.parse(savedSettings);
      this.model = model;
      this.temperature = temperature;
      console.log('AIService: Settings updated:', { model, temperature });
    }
  }
}

// Export singleton instance
export const aiService = new AIService();
