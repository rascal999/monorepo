import { openDB } from 'idb';
import { config } from '../config';

/**
 * Message cache using IndexedDB for persistence
 */
class MessageCache {
  constructor() {
    this.dbPromise = this._initDatabase();
    this.config = config.cache;
  }
  
  /**
   * Initialize the IndexedDB database
   */
  async _initDatabase() {
    return openDB('whatsapp-gui-cache', 1, {
      upgrade(db) {
        // Create messages store
        const messagesStore = db.createObjectStore('messages', {
          keyPath: ['chatId', 'messageId']
        });
        messagesStore.createIndex('byChatId', 'chatId');
        messagesStore.createIndex('byTimestamp', 'timestamp');
        
        // Create metadata store
        const metadataStore = db.createObjectStore('metadata', {
          keyPath: 'key'
        });
      }
    });
  }
  
  /**
   * Get messages with fallback to API
   */
  async getMessages(chatId, limit = 50, offset = 0, fetchFn) {
    // Skip cache if disabled
    if (!this.config.enabled) {
      return fetchFn(chatId, limit, offset);
    }
    
    try {
      // Check cache first
      const cachedMessages = await this._getCachedMessages(chatId, limit, offset);
      const metadata = await this._getMetadata(chatId);
      
      // If we have cached messages and they're not stale, return them
      if (cachedMessages && cachedMessages.length >= limit && !this._isStale(metadata)) {
        console.log(`[Cache] Using cached messages for chat ${chatId}`);
        return cachedMessages;
      }
      
      // Fetch from API if cache miss or stale
      console.log(`[Cache] Fetching fresh messages for chat ${chatId}`);
      const messages = await fetchFn(chatId, limit, offset);
      
      // Update cache
      await this._cacheMessages(chatId, messages, offset);
      
      return messages;
    } catch (error) {
      console.error('[Cache] Error getting messages:', error);
      // Fall back to API on cache error
      return fetchFn(chatId, limit, offset);
    }
  }
  
  /**
   * Get cached messages for a chat
   */
  async _getCachedMessages(chatId, limit = 50, offset = 0) {
    try {
      // Normalize chatId to ensure it's a string
      const normalizedChatId = typeof chatId === 'object' && chatId._serialized
        ? chatId._serialized
        : String(chatId);
      
      console.log('[Cache] Getting cached messages for chat:', normalizedChatId);
      
      const db = await this.dbPromise;
      const tx = db.transaction('messages', 'readonly');
      const index = tx.objectStore('messages').index('byChatId');
      
      // Get all messages for this chat
      const messages = await index.getAll(IDBKeyRange.only(normalizedChatId));
      
      // Sort by timestamp (newest first) and apply pagination
      return messages
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(offset, offset + limit);
    } catch (error) {
      console.error('[Cache] Error in _getCachedMessages:', error);
      return []; // Return empty array on error
    }
  }
  
  /**
   * Cache messages with metadata
   */
  async _cacheMessages(chatId, messages, offset = 0) {
    if (!messages || messages.length === 0) return;
    
    try {
      // Normalize chatId to ensure it's a string
      const normalizedChatId = typeof chatId === 'object' && chatId._serialized
        ? chatId._serialized
        : String(chatId);
      
      console.log('[Cache] Caching messages for chat:', normalizedChatId);
      
      const db = await this.dbPromise;
      const tx = db.transaction(['messages', 'metadata'], 'readwrite');
      
      // Store each message
      const messagesStore = tx.objectStore('messages');
      for (const message of messages) {
        // Normalize message ID to ensure it's a string
        const normalizedMessageId = typeof message.id === 'object' && message.id._serialized
          ? message.id._serialized
          : String(message.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
        
        // Create a normalized message object without circular references
        const normalizedMessage = {
          ...message,
          id: normalizedMessageId, // Replace the original ID with the normalized one
        };
        
        // Remove any potential circular references or complex objects
        delete normalizedMessage.chat; // Remove chat object if present
        
        await messagesStore.put({
          chatId: normalizedChatId,
          messageId: normalizedMessageId,
          ...normalizedMessage,
          cachedAt: Date.now()
        });
      }
      
      // Update metadata
      const metadataStore = tx.objectStore('metadata');
      await metadataStore.put({
        key: `chat:${normalizedChatId}`,
        lastUpdated: Date.now(),
        messageCount: messages.length,
        offset
      });
      
      await tx.done;
      
      // Perform cache maintenance
      this._performMaintenance();
    } catch (error) {
      console.error('[Cache] Error in _cacheMessages:', error);
    }
  }
  
  /**
   * Get metadata for a chat
   */
  async _getMetadata(chatId) {
    try {
      // Normalize chatId to ensure it's a string
      const normalizedChatId = typeof chatId === 'object' && chatId._serialized
        ? chatId._serialized
        : String(chatId);
      
      const db = await this.dbPromise;
      return await db.get('metadata', `chat:${normalizedChatId}`);
    } catch (error) {
      console.error('[Cache] Error getting metadata:', error);
      return null;
    }
  }
  
  /**
   * Check if cache is stale
   */
  _isStale(metadata) {
    if (!metadata) return true;
    
    const maxAge = this.config.messageMaxAge || 3600000; // 1 hour default
    return Date.now() - metadata.lastUpdated > maxAge;
  }
  
  /**
   * Invalidate cache for a chat
   */
  async invalidateCache(chatId) {
    try {
      // Normalize chatId to ensure it's a string
      const normalizedChatId = typeof chatId === 'object' && chatId._serialized
        ? chatId._serialized
        : String(chatId);
      
      console.log('[Cache] Invalidating cache for chat:', normalizedChatId);
      
      const db = await this.dbPromise;
      const tx = db.transaction(['messages', 'metadata'], 'readwrite');
      
      // Delete all messages for this chat
      const index = tx.objectStore('messages').index('byChatId');
      const keys = await index.getAllKeys(IDBKeyRange.only(normalizedChatId));
      const messagesStore = tx.objectStore('messages');
      
      for (const key of keys) {
        await messagesStore.delete(key);
      }
      
      // Delete metadata
      await tx.objectStore('metadata').delete(`chat:${normalizedChatId}`);
      
      await tx.done;
      return true;
    } catch (error) {
      console.error('[Cache] Error invalidating cache:', error);
      return false;
    }
  }
  
  /**
   * Prefetch next page in background
   */
  prefetchNextPage(chatId, currentOffset, limit = 50, fetchFn) {
    if (!this.config.prefetchEnabled) return;
    
    // Normalize chatId to ensure it's a string
    const normalizedChatId = typeof chatId === 'object' && chatId._serialized
      ? chatId._serialized
      : String(chatId);
    
    // Low priority background fetch
    setTimeout(async () => {
      try {
        console.log(`[Cache] Prefetching next page for chat ${normalizedChatId}`);
        const messages = await fetchFn(chatId, limit, currentOffset + limit);
        await this._cacheMessages(chatId, messages, currentOffset + limit);
      } catch (error) {
        console.error('[Cache] Error prefetching:', error);
      }
    }, 1000);
  }
  
  /**
   * Perform cache maintenance (cleanup old entries)
   */
  async _performMaintenance() {
    // Run maintenance with 10% probability to avoid doing it too often
    if (Math.random() > 0.1) return;
    
    try {
      const db = await this.dbPromise;
      
      // Get all messages sorted by cache time
      const tx = db.transaction('messages', 'readwrite');
      const index = tx.objectStore('messages').index('byTimestamp');
      const messages = await index.getAll();
      
      // Calculate total size (rough estimate)
      const totalSize = messages.reduce((size, msg) => {
        return size + JSON.stringify(msg).length;
      }, 0);
      
      // If we're over the size limit, delete oldest messages
      const maxSize = this.config.maxStorageSize || 50 * 1024 * 1024; // 50MB default
      
      if (totalSize > maxSize) {
        console.log(`[Cache] Performing maintenance, current size: ${totalSize} bytes`);
        
        // Sort by cache time (oldest first)
        messages.sort((a, b) => a.cachedAt - b.cachedAt);
        
        // Delete oldest messages until we're under the limit
        let currentSize = totalSize;
        const messagesStore = tx.objectStore('messages');
        
        for (const message of messages) {
          if (currentSize <= maxSize * 0.8) break; // Stop when we're under 80% of the limit
          
          const messageSize = JSON.stringify(message).length;
          
          try {
            await messagesStore.delete([message.chatId, message.messageId]);
            currentSize -= messageSize;
          } catch (error) {
            console.error('[Cache] Error deleting message during maintenance:', error);
            // Try with normalized IDs if the direct delete fails
            try {
              // Normalize IDs to ensure they're strings
              const normalizedChatId = typeof message.chatId === 'object' && message.chatId._serialized
                ? message.chatId._serialized
                : String(message.chatId);
              
              const normalizedMessageId = typeof message.messageId === 'object' && message.messageId._serialized
                ? message.messageId._serialized
                : String(message.messageId);
              
              await messagesStore.delete([normalizedChatId, normalizedMessageId]);
              currentSize -= messageSize;
            } catch (innerError) {
              console.error('[Cache] Error deleting message with normalized IDs:', innerError);
            }
          }
        }
      }
      
      await tx.done;
    } catch (error) {
      console.error('[Cache] Error during maintenance:', error);
    }
  }
  
  /**
   * Clear all cached data
   */
  async clearAll() {
    try {
      const db = await this.dbPromise;
      const tx = db.transaction(['messages', 'metadata'], 'readwrite');
      
      await tx.objectStore('messages').clear();
      await tx.objectStore('metadata').clear();
      
      await tx.done;
      return true;
    } catch (error) {
      console.error('[Cache] Error clearing cache:', error);
      return false;
    }
  }
}

// Create and export cache instance
const messageCache = new MessageCache();
export default messageCache;