import axios from 'axios';
import { config } from '../config';

/**
 * Client for interacting with Ollama API for chat analysis
 */
class OllamaClient {
  constructor() {
    this.baseUrl = config.ollama.url;
    this.model = config.ollama.model;
    
    // Create axios instance with default config
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('Ollama API Error:', error.response || error);
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Update client configuration
   */
  updateConfig(newConfig) {
    this.baseUrl = newConfig.ollama.url;
    this.model = newConfig.ollama.model;
    
    // Update axios instance
    this.client.defaults.baseURL = this.baseUrl;
  }
  
  /**
   * Analyze sentiment of messages
   */
  async analyzeSentiment(messages) {
    const prompt = this._createSentimentPrompt(messages);
    return this._analyzeWithOllama(prompt);
  }
  
  /**
   * Analyze relationship dynamics from messages
   */
  async analyzeRelationship(messages) {
    const prompt = this._createRelationshipPrompt(messages);
    return this._analyzeWithOllama(prompt);
  }
  
  /**
   * Generate suggested responses
   */
  async generateResponses(messages, count = 3) {
    const prompt = this._createResponsesPrompt(messages, count);
    return this._analyzeWithOllama(prompt);
  }
  
  /**
   * Send prompt to Ollama for analysis
   */
  async _analyzeWithOllama(prompt, model = null) {
    try {
      // Use provided model or fall back to instance model
      const modelToUse = model || this.model;
      
      const data = {
        model: modelToUse,
        prompt: prompt,
        stream: false
      };
      
      const response = await this.client.post('/api/generate', data);
      return response.data.response;
    } catch (error) {
      console.error('Error analyzing with Ollama:', error);
      throw error;
    }
  }
  
  /**
   * Create prompt for sentiment analysis
   */
  _createSentimentPrompt(messages) {
    const messageText = messages
      .map(msg => `${msg.fromMe ? 'Me' : 'Them'}: ${msg.body}`)
      .join('\n');
    
    return `
      Analyze the sentiment and emotional tone of the following conversation.
      Provide an overall sentiment (positive, negative, neutral, mixed),
      a sentiment score from 0-10, the dominant emotions present,
      and a brief summary of the emotional tone.
      Format your response as JSON with the following structure:
      {
        "sentiment": "positive/negative/neutral/mixed",
        "score": 7,
        "emotions": ["joy", "excitement"],
        "summary": "The conversation has a generally positive tone..."
      }
      
      CONVERSATION:
      ${messageText}
    `;
  }
  
  /**
   * Create prompt for relationship analysis
   */
  _createRelationshipPrompt(messages) {
    const messageText = messages
      .map(msg => `${msg.fromMe ? 'Me' : 'Them'}: ${msg.body}`)
      .join('\n');
    
    return `
      Analyze the relationship dynamics in the following conversation.
      Assess the quality of the relationship, communication style,
      level of engagement, key topics, and provide recommendations
      for improving communication if needed.
      Format your response as JSON with the following structure:
      {
        "quality": "strong/moderate/strained",
        "communication": "open/guarded/mixed",
        "engagement": "high/medium/low",
        "topics": ["work", "personal"],
        "recommendations": ["Be more direct", "Ask more questions"],
        "summary": "The relationship appears to be..."
      }
      
      CONVERSATION:
      ${messageText}
    `;
  }
  
  /**
   * Create prompt for generating suggested responses
   */
  _createResponsesPrompt(messages, count = 3) {
    const messageText = messages
      .map(msg => `${msg.fromMe ? 'Me' : 'Them'}: ${msg.body}`)
      .join('\n');
    
    return `
      Based on the following conversation, generate ${count} contextually
      appropriate responses that I could send next. For each response,
      provide a description of its tone and purpose.
      Format your response as JSON with the following structure:
      {
        "responses": [
          {
            "text": "Sure, I'd be happy to help with that!",
            "tone": "helpful",
            "purpose": "offering assistance"
          },
          {
            "text": "I'm not available right now, can we discuss this later?",
            "tone": "polite but firm",
            "purpose": "setting boundaries"
          }
        ]
      }
      
      CONVERSATION:
      ${messageText}
    `;
  }
}

// Create and export Ollama client instance
const ollama = new OllamaClient();
export default ollama;