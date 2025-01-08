import { aiSettingsService } from './settingsService';
import { requestService } from './requestService';
import { definitionService } from './definitionService';
import { chatService } from './chatService';
import { sourceService } from './sourceService';

class AIService {
  constructor() {
    this.settings = aiSettingsService;
    this.request = requestService;
    this.definition = definitionService;
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
    return this.definition.getDefinitions(terms, context);
  }

  queueDefinitionRequest(term, context, callback) {
    return this.definition.queueDefinitionRequest(term, context, callback);
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
