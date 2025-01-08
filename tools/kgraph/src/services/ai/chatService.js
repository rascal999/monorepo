import { fetchChatCompletion } from '../openRouterApi';
import { aiSettingsService } from './settingsService';

class ChatService {
  constructor() {
    this.systemPrompt = `You are a knowledgeable assistant helping to define concepts and explain their relationships. When given a term or concept:
1. Provide a clear, concise definition
2. Explain key aspects and relationships
3. Use academic/technical language when appropriate
4. Keep responses focused and relevant
5. Aim for 2-3 paragraphs maximum`;
  }

  async getChatResponse(messages, context = '', onStream) {
    console.log('ChatService: Getting chat response:', { context, messageCount: messages.length });
    
    const fullMessages = [
      { 
        role: 'system', 
        content: `${this.systemPrompt}\nContext: ${context}`
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
