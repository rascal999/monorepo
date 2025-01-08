import { fetchChatCompletion } from '../openRouterApi';
import { aiSettingsService } from './settingsService';

class SourceService {
  constructor() {
    this.systemPrompt = 'Search the web for recent and reliable sources on the given topic. Return a list of URLs with titles and brief descriptions. Focus on academic, scientific, or reputable sources. Format response as JSON array with objects containing url, title, and description fields.';
  }

  async searchSources(keyword) {
    console.log('SourceService: Searching sources for:', keyword);
    
    const messages = [
      {
        role: 'system',
        content: this.systemPrompt
      },
      {
        role: 'user',
        content: `Search for sources about: ${keyword}`
      }
    ];

    try {
      const response = await fetchChatCompletion(
        messages, 
        aiSettingsService.getModel()
      );
      console.log('SourceService: Sources received');
      
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
      console.error('SourceService: Error searching sources:', error);
      return {
        success: false,
        error: error.message || 'Failed to search sources'
      };
    }
  }
}

export const sourceService = new SourceService();
