class RequestService {
  constructor() {
    this.batchQueue = new Map(); // Map of term -> array of callbacks
    this.batchTimeout = null;
    this.BATCH_DELAY = 50; // Minimal delay to prevent race conditions
    this.activeRequests = new Set(); // Track active requests to prevent duplicates
  }

  clearStaleRequests() {
    console.log('RequestService: Clearing stale requests:', {
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

  isRequestActive(requestId) {
    return this.activeRequests.has(requestId);
  }

  addActiveRequest(requestId) {
    this.activeRequests.add(requestId);
  }

  removeActiveRequest(requestId) {
    this.activeRequests.delete(requestId);
  }

  queueRequest(requestId, callback, processor) {
    console.log('RequestService: Processing request:', {
      requestId,
      activeRequests: [...this.activeRequests]
    });

    // Process request with minimal delay to allow for state updates
    setTimeout(async () => {
      // Skip if request is already in progress
      if (this.isRequestActive(requestId)) {
        console.log('RequestService: Skipping duplicate request:', requestId);
        callback({
          success: false,
          error: 'Duplicate request skipped'
        });
        return;
      }

      this.addActiveRequest(requestId);
      
      try {
        const result = await processor();
        callback(result);
      } catch (error) {
        console.error('RequestService: Processing error:', error);
        callback({
          success: false,
          error: error.message || 'Request failed'
        });
      } finally {
        this.removeActiveRequest(requestId);
      }
    }, this.BATCH_DELAY);
  }
}

export const requestService = new RequestService();
