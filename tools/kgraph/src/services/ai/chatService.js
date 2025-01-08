import { fetchChatCompletion } from '../openRouterApi';
import { aiSettingsService } from './settingsService';

class ChatService {
  constructor() {
    this.systemPrompt = `You are a knowledgeable assistant helping to define concepts and explain their relationships.`;
    this.definitionPrompt = `Define {term} in the context of {context}. Start with a bold summary sentence. Then add 2-3 bullet points with key details. Keep it simple and clear.`;
  }

  async getDefinition(term, context = '') {
    console.log('ChatService: Getting definition for:', { 
      term, 
      context,
      prompt: this.definitionPrompt.replace('{term}', term).replace('{context}', context)
    });
    
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
      console.log('ChatService: Definition received:', {
        success: true,
        content: response.content
      });
      return {
        success: true,
        message: { role: 'assistant', content: response.content, isDefinition: true }
      };
    } catch (error) {
      console.error('ChatService: Error getting definition:', {
        error: error.message,
        term,
        context
      });
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
