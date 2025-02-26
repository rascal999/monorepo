# AnythingLLM Agent Skills Secrets Management

This document explains how secrets are managed for AnythingLLM agent skills.

## Overview

Instead of storing credentials in each skill's `plugin.json` file, this system loads credentials from a central repository at runtime. This approach:

- Removes sensitive data from the code repository
- Provides a single source of truth for credentials
- Makes credential rotation easier
- Improves security

## How It Works

1. The `anythingllm.nix` file mounts the secrets directory from `/home/user/git/github/monorepo/secrets/environments/mgp/env` into the Docker container at `/app/server/storage/secrets/env`
2. The `SECRETS_PATH` environment variable is set to point to this file
3. The `load-secrets.js` utility loads secrets from this file and maps them to skill-specific credential names
4. Skill handlers use the `load-secrets.js` utility to get secrets instead of reading them from `plugin.json` files

## Directory Structure

```
/home/user/git/github/monorepo/
  ├── secrets/
  │   └── environments/
  │       └── mgp/
  │           └── env                 # Central secrets file
  └── tools/
      └── anythingllm/
          └── agent-skills/
              ├── utils/
              │   └── load-secrets.js # Utility to load secrets
              ├── jira-create/
              │   ├── plugin.json     # No secrets stored here
              │   └── handler.js      # Uses load-secrets.js
              └── slack-channel-reader/
                  ├── plugin.json     # No secrets stored here
                  └── handler.js      # Uses load-secrets.js
```

## Secret Mapping

The `load-secrets.js` utility maps skill-specific credential names to central repository names:

```javascript
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
```

## Usage in Skill Handlers

Skill handlers use the `load-secrets.js` utility to get secrets:

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

## Adding Support for New Skills

To add support for additional skills, update the `CREDENTIAL_MAP` in `load-secrets.js`:

```javascript
const CREDENTIAL_MAP = {
  // Existing mappings...
  
  // Add new skill mapping here
  'new-skill-id': {
    'SKILL_CREDENTIAL': 'CENTRAL_CREDENTIAL'
  }
};
```

## Debugging

If you encounter issues with secrets loading, you can enable debugging by setting the `DEBUG_SECRETS` environment variable to `true`:

```javascript
// In your handler function
process.env.DEBUG_SECRETS = 'true';
const loadSecrets = require('../utils/load-secrets');
```

This will output additional information about the secrets loading process.