import dns from 'dns';
import https from 'https';
import { NETWORK_CONFIG } from '../config/config.js';

// Create HTTPS agent with custom configuration
export const httpsAgent = new https.Agent(NETWORK_CONFIG.https);

/**
 * Sleep for a specified duration
 * @param {number} ms - Duration in milliseconds
 * @returns {Promise<void>}
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate backoff delay for retries
 * @param {number} attempt - Current attempt number
 * @returns {number} Delay in milliseconds
 */
export function calculateBackoff(attempt) {
  const delay = Math.min(
    NETWORK_CONFIG.retryDelayMs * Math.pow(2, attempt - 1),
    NETWORK_CONFIG.maxRetryDelayMs
  );
  return delay;
}

/**
 * Resolve hostname using configured DNS servers
 * @param {string} hostname - The hostname to resolve
 * @returns {Promise<string[]>} Array of resolved IP addresses
 */
export async function resolveHostname(hostname) {
  return new Promise((resolve, reject) => {
    // Set DNS servers
    dns.setServers(NETWORK_CONFIG.dnsServers);

    dns.resolve4(hostname, (err, addresses) => {
      if (err) {
        console.error('DNS resolution failed:', err);
        reject(err);
        return;
      }
      resolve(addresses);
    });
  });
}

/**
 * Log network status information
 */
export function logNetworkInfo() {
  console.log('Network configuration:', {
    dnsServers: NETWORK_CONFIG.dnsServers,
    retryAttempts: NETWORK_CONFIG.retryAttempts,
    retryDelayMs: NETWORK_CONFIG.retryDelayMs,
    maxRetryDelayMs: NETWORK_CONFIG.maxRetryDelayMs,
    httpsConfig: NETWORK_CONFIG.https
  });
}
