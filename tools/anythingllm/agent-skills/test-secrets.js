#!/usr/bin/env node

/**
 * Test Secrets Utility
 * 
 * This script tests the load-secrets utility by loading secrets
 * for the Jira and Slack skills.
 */

const loadSecrets = require('./utils/load-secrets');

// Test skills
const skills = [
  'jira-create',
  'slack-channel-reader'
];

console.log('Testing Load Secrets Utility\n');

// Test each skill
skills.forEach(skillId => {
  console.log(`Skill: ${skillId}`);
  
  // Get secrets for this skill
  const secrets = loadSecrets.getSecretsForSkill(skillId);
  
  // Display secrets (keys only, not values)
  if (Object.keys(secrets).length === 0) {
    console.log('  No secrets found');
  } else {
    Object.keys(secrets).forEach(key => {
      // Show key and masked value
      const maskedValue = secrets[key] ? '********' : 'undefined';
      console.log(`  ${key}: ${maskedValue}`);
    });
  }
  
  console.log('');
});

// Display all available secrets in the central repository
console.log('Available Secrets in Central Repository:');
const allSecrets = loadSecrets.loadAllSecrets();
if (Object.keys(allSecrets).length === 0) {
  console.log('  No secrets found in central repository');
} else {
  Object.keys(allSecrets).forEach(key => {
    // Show key only, not value
    console.log(`  ${key}`);
  });
}

console.log('\nDone!');