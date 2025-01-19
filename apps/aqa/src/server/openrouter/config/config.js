// OpenRouter API configuration
export const API_CONFIG = {
  url: 'https://api.openrouter.ai/api/v1/chat/completions',
  model: 'openai/gpt-4',
  temperature: 0.7, // Increased for more creative and diverse questions
  maxTokens: 2000, // Reduced to stay within context length limit
  headers: {
    'Content-Type': 'application/json',
    'HTTP-Referer': 'http://localhost:3001',
    'X-Title': 'AQA Quiz Generator',
    'User-Agent': 'AQA/1.0.0'
  }
};

// Network configuration
export const NETWORK_CONFIG = {
  // Primary DNS servers
  dnsServers: [
    '8.8.8.8',   // Google primary
    '8.8.4.4',   // Google secondary
    '1.1.1.1',   // Cloudflare primary
    '1.0.0.1',   // Cloudflare secondary
    '208.67.222.222', // OpenDNS primary
    '208.67.220.220'  // OpenDNS secondary
  ],

  // Retry configuration
  retryAttempts: 3,
  retryDelayMs: 1000,
  maxRetryDelayMs: 8000,

  // HTTPS configuration
  https: {
    keepAlive: true,
    keepAliveMsecs: 1000,
    timeout: 10000,
    rejectUnauthorized: false // Allow self-signed certs in development
  },

  // WSL-specific configuration
  wsl: {
    // Common WSL network addresses
    hostAddresses: [
      '172.17.0.1',  // Default Docker network
      '172.18.0.1',  // Alternative Docker network
      '192.168.1.1'  // Common router address
    ],
    // Fallback proxy ports
    proxyPorts: [8080, 3128, 1080]
  }
};
