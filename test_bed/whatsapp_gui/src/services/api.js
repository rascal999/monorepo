import axios from 'axios';
import { config } from '../config';

/**
 * API client for WhatsApp backend
 */
class ApiClient {
  constructor() {
    console.log('Config object:', config);
    console.log('WhatsApp config:', config.whatsapp);
    
    this.baseUrl = config.whatsapp.baseUrl;
    this.apiKey = config.whatsapp.apiKey;
    this.sessionId = config.whatsapp.sessionId;
    
    console.log('Session ID:', this.sessionId);
    
    // Create axios instance with default config
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey
      }
    });
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error.response || error);
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Update client configuration
   */
  updateConfig(newConfig) {
    console.log('Updating config with:', newConfig);
    
    this.baseUrl = newConfig.whatsapp.baseUrl;
    this.apiKey = newConfig.whatsapp.apiKey;
    this.sessionId = newConfig.whatsapp.sessionId;
    
    console.log('Updated session ID:', this.sessionId);
    
    // Update axios instance
    this.client.defaults.baseURL = this.baseUrl;
    this.client.defaults.headers['x-api-key'] = this.apiKey;
  }
  
  /**
   * Check if session exists
   */
  async checkSession() {
    try {
      console.log('Checking session with ID:', this.sessionId);
      // Use hardcoded session ID "ABCD"
      const url = `/session/status/ABCD`;
      console.log('Request URL:', url);
      const response = await this.client.get(url);
      return response.data.state === 'CONNECTED';
    } catch (error) {
      console.error('Error checking session:', error);
      return false;
    }
  }
  
  /**
   * Start a new session
   */
  async startSession() {
    try {
      // Use hardcoded session ID "ABCD"
      const response = await this.client.get(`/session/start/ABCD`);
      return response.data;
    } catch (error) {
      console.error('Error starting session:', error);
      throw error;
    }
  }
  
  /**
   * Wait for session connection
   */
  async waitForConnection(timeout = 60000, interval = 1000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const connected = await this.checkSession();
        if (connected) {
          return true;
        }
        
        // Wait before next check
        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        console.error('Error waiting for connection:', error);
      }
    }
    
    return false;
  }
  
  /**
   * Get all contacts
   */
  async getContacts() {
    try {
      // Use hardcoded session ID "ABCD"
      const response = await this.client.get(`/client/getContacts/ABCD`);
      return response.data.contacts || [];
    } catch (error) {
      console.error('Error fetching contacts:', error);
      throw error;
    }
  }
  
  /**
   * Get all chats
   */
  async getChats() {
    try {
      // Use hardcoded session ID "ABCD"
      const response = await this.client.get(`/client/getChats/ABCD`);
      return response.data.chats || [];
    } catch (error) {
      console.error('Error fetching chats:', error);
      throw error;
    }
  }
  
  // Track last fetch time and chat ID to prevent spam
  lastFetchTime = 0;
  lastChatId = null;
  
  /**
   * Get messages for a chat
   */
  async getMessages(chatId, limit = 50) {
    try {
      // Extract the serialized chatId if it's an object
      const chatIdToUse = typeof chatId === 'object' && chatId._serialized
        ? chatId._serialized
        : chatId;
      
      // Implement debounce to prevent spam
      const now = Date.now();
      if (chatIdToUse === this.lastChatId && now - this.lastFetchTime < 2000) {
        console.log('Skipping fetch, too recent:', now - this.lastFetchTime, 'ms since last fetch');
        return []; // Return empty array to prevent UI issues
      }
      
      // Update tracking variables
      this.lastFetchTime = now;
      this.lastChatId = chatIdToUse;
      
      console.log('Fetching messages for chatId:', chatIdToUse);
      
      // Use hardcoded session ID "ABCD"
      const response = await this.client.post(`/chat/fetchMessages/ABCD`, {
        chatId: chatIdToUse,
        searchOptions: {
          limit
        }
      });
      return response.data.messages || [];
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  }
  
  /**
   * Send a message
   */
  async sendMessage(chatId, message) {
    try {
      // Use hardcoded session ID "ABCD"
      // Extract the serialized chatId if it's an object
      const chatIdToUse = typeof chatId === 'object' && chatId._serialized
        ? chatId._serialized
        : chatId;
      
      console.log('Sending message to chatId:', chatIdToUse);
      
      const response = await this.client.post(`/client/sendMessage/ABCD`, {
        chatId: chatIdToUse,
        contentType: 'string',
        content: message
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }
  
  /**
   * Find contact by name or number
   */
  async findContact(query) {
    try {
      // First try to get all contacts and filter locally
      const contacts = await this.getContacts();
      
      // Try exact name match
      const nameMatch = contacts.find(contact =>
        contact.name && contact.name.toLowerCase() === query.toLowerCase()
      );
      if (nameMatch) return nameMatch;
      
      // Try number match
      const numberMatch = contacts.find(contact =>
        contact.number && contact.number === query.replace('+', '')
      );
      if (numberMatch) return numberMatch;
      
      // If no match found, try to get contact by ID if it looks like a phone number
      if (query.replace('+', '').match(/^\d+$/)) {
        const contactId = `${query.replace('+', '')}@c.us`;
        // Use hardcoded session ID "ABCD"
        const response = await this.client.post(`/client/getContactById/ABCD`, {
          contactId
        });
        return response.data.contact;
      }
      
      return null;
    } catch (error) {
      console.error('Error finding contact:', error);
      throw error;
    }
  }
}

// Create and export API client instance
const api = new ApiClient();
export default api;