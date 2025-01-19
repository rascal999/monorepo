import { NETWORK_CONFIG } from '../config/config.js';

/**
 * Detects and configures proxy settings for WSL environment
 * @returns {Object|null} Proxy configuration if detected, null otherwise
 */
export function detectWslProxy() {
  try {
    // Check if running in WSL
    const isWsl = process.platform === 'linux' && process.env.WSL_DISTRO_NAME;
    if (!isWsl) {
      return null;
    }

    console.log('WSL environment detected, checking proxy configuration...');

    // Try common WSL host addresses and proxy ports
    for (const hostAddress of NETWORK_CONFIG.wsl.hostAddresses) {
      for (const proxyPort of NETWORK_CONFIG.wsl.proxyPorts) {
        try {
          const proxyUrl = `http://${hostAddress}:${proxyPort}`;
          console.log(`Testing proxy: ${proxyUrl}`);
          
          // TODO: Add actual proxy test logic here
          // For now, just return the first combination
          return {
            host: hostAddress,
            port: proxyPort,
            url: proxyUrl
          };
        } catch (error) {
          console.log(`Proxy ${hostAddress}:${proxyPort} not available:`, error.message);
          continue;
        }
      }
    }

    console.log('No working proxy configuration found');
    return null;
  } catch (error) {
    console.error('Error detecting WSL proxy:', error);
    return null;
  }
}
