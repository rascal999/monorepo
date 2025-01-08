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
      if (request.timeoutId) {
        clearTimeout(request.timeoutId);
      }
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

    console.log('RequestService: After clearing stale requests:', {
      activeRequests: [...this.activeRequests],
      queueSize: this.batchQueue.size
    });
  }

  isRequestActive(requestId) {
    const isActive = this.activeRequests.has(requestId);
    console.log('RequestService: Checking if request is active:', {
      requestId,
      isActive,
      activeRequests: [...this.activeRequests]
    });
    return isActive;
  }

  addActiveRequest(requestId) {
    console.log('RequestService: Adding active request:', {
      requestId,
      currentActiveRequests: [...this.activeRequests]
    });
    this.activeRequests.add(requestId);
  }

  removeActiveRequest(requestId) {
    console.log('RequestService: Removing active request:', {
      requestId,
      currentActiveRequests: [...this.activeRequests]
    });
    this.activeRequests.delete(requestId);
  }

  queueRequest(requestId, callback, processor) {
    console.log('RequestService: Processing request:', {
      requestId,
      activeRequests: [...this.activeRequests]
    });

    // Clean up any stale request with this ID first
    this.removeActiveRequest(requestId);
    this.addActiveRequest(requestId);

    // Store request info
    const request = {
      timeoutId: null,
      callbacks: [{ callback }],
      isProcessing: false
    };
    this.batchQueue.set(requestId, request);

    // Process request with minimal delay to allow for state updates
    request.timeoutId = setTimeout(async () => {
      try {
        console.log('RequestService: Starting request processing:', {
          requestId,
          isActive: this.isRequestActive(requestId)
        });

        request.isProcessing = true;
        const result = await processor();

        console.log('RequestService: Request processor completed:', {
          requestId,
          isActive: this.isRequestActive(requestId),
          success: result?.success
        });

        // Only consider request cancelled if it was explicitly removed
        if (!this.isRequestActive(requestId) && !request.isProcessing) {
          console.log('RequestService: Request was cancelled:', requestId);
          callback({
            success: false,
            error: 'Request was cancelled'
          });
          return;
        }

        callback(result);
      } catch (error) {
        console.error('RequestService: Processing error:', error);
        callback({
          success: false,
          error: error.message || 'Request failed'
        });
      } finally {
        request.isProcessing = false;
        // Clean up request state
        this.removeActiveRequest(requestId);
        this.batchQueue.delete(requestId);
        
        // Log current state after cleanup
        console.log('RequestService: Request completed:', {
          requestId,
          remainingActiveRequests: [...this.activeRequests],
          remainingQueueSize: this.batchQueue.size
        });
      }
    }, this.BATCH_DELAY);
  }
}

export const requestService = new RequestService();
