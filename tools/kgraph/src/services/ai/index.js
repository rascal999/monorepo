import { aiSettingsService } from './settingsService';
import { requestService } from './requestService';
import { chatService } from './chatService';
import { sourceService } from './sourceService';

class AIService {
  constructor() {
    this.settings = aiSettingsService;
    this.request = requestService;
    this.chat = chatService;
    this.source = sourceService;
  }

  // Settings management
  updateSettings() {
    this.settings.updateSettings();
  }

  // Request management
  clearStaleRequests() {
    this.request.clearStaleRequests();
  }

  // Definition operations
  getDefinitions(terms, context = '') {
    return Promise.all(terms.map(term => this.chat.getDefinition(term, context)));
  }

  // Chat operations
  getChatResponse(messages, context = '', onStream) {
    return this.chat.getChatResponse(messages, context, onStream);
  }

  // Source operations
  searchSources(keyword) {
    return this.source.searchSources(keyword);
  }
}

// Export singleton instance
export const aiService = new AIService();
