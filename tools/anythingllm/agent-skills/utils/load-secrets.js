/**
 * Load Secrets Utility
 * 
 * This utility loads secrets from the central secrets repository
 * for use in AnythingLLM agent skills.
 */

const fs = require('fs');
const path = require('path');

// Path to the central secrets repository
// When running in the AnythingLLM container, this will be set to /app/server/storage/secrets/env
// Otherwise, it will fall back to the relative path from the repository root
const SECRETS_PATH = process.env.SECRETS_PATH || '/app/server/storage/secrets/env';

// For debugging
const DEBUG = true; // Always enable debugging for now

/**
 * Parse an env file into an object
 */
function parseEnvFile(content) {
  const result = {};
  const lines = content.split('\n');
  
  for (const line of lines) {
    // Skip comments and empty lines
    if (line.trim().startsWith('#') || !line.trim()) {
      continue;
    }
    
    // Parse key-value pairs
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) {
      const key = match[1].trim();
      let value = match[2].trim();
      
      // Remove quotes if present
      if ((value.startsWith('"') && value.endsWith('"')) || 
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.substring(1, value.length - 1);
      }
      
      result[key] = value;
    }
  }
  
  return result;
}

/**
 * Load all secrets from the central repository
 */
function loadAllSecrets() {
  try {
    // First try absolute path (for container environment)
    if (SECRETS_PATH.startsWith('/')) {
      if (DEBUG) console.log(`Trying absolute path: ${SECRETS_PATH}`);
      if (fs.existsSync(SECRETS_PATH)) {
        if (DEBUG) console.log(`Found secrets file at absolute path: ${SECRETS_PATH}`);
        const envContent = fs.readFileSync(SECRETS_PATH, 'utf8');
        return parseEnvFile(envContent);
      }
    }
    
    // Then try relative path (for development environment)
    const envPath = path.resolve(__dirname, SECRETS_PATH);
    if (DEBUG) console.log(`Trying relative path: ${envPath}`);
    if (fs.existsSync(envPath)) {
      if (DEBUG) console.log(`Found secrets file at relative path: ${envPath}`);
      const envContent = fs.readFileSync(envPath, 'utf8');
      return parseEnvFile(envContent);
    }
    
    console.warn(`Secrets file not found at ${SECRETS_PATH} or ${envPath}`);
    return {};
  } catch (error) {
    console.error('Error loading secrets:', error);
    return {};
  }
}

/**
 * Get secrets for a specific skill
 */
function getSecretsForSkill(skillId) {
  const secrets = loadAllSecrets();
  const skillSecrets = {};
  
  try {
    // Dynamically load the plugin.json for this skill
    const pluginJsonPath = path.resolve(__dirname, `../${skillId}/plugin.json`);
    if (DEBUG) console.log(`Looking for plugin.json at: ${pluginJsonPath}`);
    
    if (fs.existsSync(pluginJsonPath)) {
      if (DEBUG) console.log(`Found plugin.json for ${skillId}`);
      const pluginJson = JSON.parse(fs.readFileSync(pluginJsonPath, 'utf8'));
      
      // Extract required credentials from setup_args field
      const setupArgs = pluginJson.setup_args || {};
      if (DEBUG) console.log(`Setup args for ${skillId}:`, Object.keys(setupArgs));
      
      // Get all credential keys from setup_args
      const credentialKeys = Object.keys(setupArgs);
      
      // Map each credential to its value in the secrets file
      credentialKeys.forEach(credKey => {
        if (secrets[credKey]) {
          skillSecrets[credKey] = secrets[credKey];
          if (DEBUG) console.log(`Found secret ${credKey} for ${skillId}`);
        } else if (DEBUG) {
          console.log(`Secret ${credKey} not found for ${skillId}`);
        }
      });
      
      // Special case mappings for certain skills
      if (skillId === 'slack-channel-reader' && credentialKeys.includes('SLACK_TOKEN') && secrets['SLACK_USER_READ_API_TOKEN']) {
        skillSecrets['SLACK_TOKEN'] = secrets['SLACK_USER_READ_API_TOKEN'];
        if (DEBUG) console.log(`Mapped SLACK_USER_READ_API_TOKEN to SLACK_TOKEN for slack-channel-reader`);
      }
    } else if (DEBUG) {
      console.log(`Plugin.json not found for ${skillId}`);
    }
  } catch (error) {
    console.error(`Error loading plugin.json for ${skillId}:`, error);
  }
  
  return skillSecrets;
}

module.exports = {
  loadAllSecrets,
  getSecretsForSkill
};