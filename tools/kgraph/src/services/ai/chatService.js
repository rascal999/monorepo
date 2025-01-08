import { fetchChatCompletion } from '../openRouterApi';
import { aiSettingsService } from './settingsService';

class ChatService {
  constructor() {
    this.systemPrompt = `You are a knowledgeable assistant helping to define concepts and explain their relationships.`;
    this.definitionPrompt = `Define {term} in the context of {context}. Start with one concise summary sentence in **bold**. Then provide more detailed explanation. Use markdown for clarity (*italic*, bullet points). No conversational phrases. No parentheses around terms. Total response must be under 120 words.`;
  }

  async getDefinition(term, context = '') {
    console.log('ChatService: Getting definition for:', { term, context });
    
    const messages = [
      { 
        role: 'system', 
        content: this.definitionPrompt.replace('{term}', term).replace('{context}', context)
      },
      {
        role: 'user',
        content: `Define and explain: ${term}`
      }
    ];

    try {
      const response = await fetchChatCompletion(
        messages, 
        aiSettingsService.getModel()
      );
      console.log('ChatService: Definition received');
      return {
        success: true,
        message: { role: 'assistant', content: response.content, isDefinition: true }
      };
    } catch (error) {
      console.error('ChatService: Error getting definition:', error);
      return {
        success: false,
        error: error.message || 'Failed to get definition'
      };
    }
  }

  async getChatResponse(messages, context = '', onStream, isDefinitionRequest = false) {
    console.log('ChatService: Getting chat response:', { context, messageCount: messages.length });
    
    // For regular chat, add context about previous messages
    const fullMessages = [
      { 
        role: 'system', 
        content: `${this.systemPrompt}\nContext: ${context}\n${isDefinitionRequest ? '' : 'Previous messages contain the initial definition. Continue the conversation naturally.'}`
      },
      ...messages
    ];

    try {
      if (onStream) {
        // For streaming, we'll accumulate the full response
        let fullContent = '';
        await fetchChatCompletion(
          fullMessages, 
          aiSettingsService.getModel(), 
          (content) => {
            fullContent += content;
            onStream({
              success: true,
              message: { role: 'assistant', content: fullContent }
            });
          }
        );
        return {
          success: true,
          message: { role: 'assistant', content: fullContent }
        };
      } else {
        // Non-streaming response
        const response = await fetchChatCompletion(
          fullMessages, 
          aiSettingsService.getModel()
        );
        console.log('ChatService: Chat response received');
        return {
          success: true,
          message: response
        };
      }
    } catch (error) {
      console.error('ChatService: Error getting chat response:', error);
      return {
        success: false,
        error: error.message || 'Failed to get response'
      };
    }
  }
}

export const chatService = new ChatService();
