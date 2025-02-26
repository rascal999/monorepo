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
const SECRETS_PATH = process.env.SECRETS_PATH || '../../../../../secrets/environments/mgp/env';

// For debugging
const DEBUG = process.env.DEBUG_SECRETS === 'true';

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

// Mapping of skill credentials to central repository credentials
const CREDENTIAL_MAP = {
  'jira-create': {
    'JIRA_HOST': 'JIRA_URL',
    'JIRA_EMAIL': 'JIRA_EMAIL',
    'JIRA_API_TOKEN': 'JIRA_API_TOKEN'
  },
  'slack-channel-reader': {
    'SLACK_TOKEN': 'SLACK_USER_READ_API_TOKEN'
  }
  // Add mappings for other skills as needed
};

/**
 * Get secrets for a specific skill
 */
function getSecretsForSkill(skillId) {
  const secrets = loadAllSecrets();
  const mapping = CREDENTIAL_MAP[skillId] || {};
  const skillSecrets = {};
  
  // Map secrets from central store to skill-specific names
  Object.entries(mapping).forEach(([skillKey, secretKey]) => {
    if (secrets[secretKey]) {
      skillSecrets[skillKey] = secrets[secretKey];
      if (DEBUG) console.log(`Mapped ${secretKey} to ${skillKey}`);
    } else if (DEBUG) {
      console.log(`Secret ${secretKey} not found for ${skillKey}`);
    }
  });
  
  return skillSecrets;
}

module.exports = {
  loadAllSecrets,
  getSecretsForSkill
};