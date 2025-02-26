# Changes Made to AnythingLLM Agent Skills

## Overview

This update centralizes credentials for AnythingLLM agent skills by:

1. Removing credentials from plugin.json files
2. Creating a utility to load credentials from the central secrets repository
3. Updating handlers to use the utility

## Files Modified

1. **plugin.json files**
   - Removed credential values from:
     - `jira-create/plugin.json`
     - `slack-channel-reader/plugin.json`

2. **handler.js files**
   - Updated to use the load-secrets utility:
     - `jira-create/handler.js`
     - `slack-channel-reader/handler.js`

## Files Created

1. **load-secrets.js**
   - Loads secrets from the central repository
   - Maps skill-specific credential names to central repository names
   - Provides a simple API for getting secrets for a specific skill

2. **usage-example.js**
   - Shows how to use the load-secrets utility in a skill handler

3. **README.md**
   - Explains how to use the load-secrets utility
   - Documents the API and supported skills

4. **test-secrets.js**
   - Tests the load-secrets utility by loading secrets for the Jira and Slack skills

## How It Works

1. The `load-secrets.js` utility loads secrets from the central repository at `../../../../../secrets/environments/mgp/env`
2. It maps skill-specific credential names to central repository names (e.g., `JIRA_HOST` -> `JIRA_URL`)
3. Skill handlers check if credentials are available in `runtimeArgs`, and if not, load them from the central repository

## Usage

To use the load-secrets utility in a skill handler:

```javascript
const loadSecrets = require('../utils/load-secrets');

// In your handler function
let credentials = this.runtimeArgs || {};

// If credentials are not in runtimeArgs, get them from secrets
if (!credentials.CREDENTIAL_NAME) {
  const skillId = this.config?.hubId || 'your-skill-id';
  const skillSecrets = loadSecrets.getSecretsForSkill(skillId);
  credentials = {
    ...skillSecrets,
    ...credentials
  };
}

// Use credentials
const { CREDENTIAL_NAME } = credentials;
```

## Testing

Run the test script to verify that the load-secrets utility works:

```bash
node test-secrets.js