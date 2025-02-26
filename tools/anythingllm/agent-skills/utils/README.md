# AnythingLLM Agent Skills Utilities

This directory contains utilities for AnythingLLM agent skills.

## Files

- `load-secrets.js` - Utility for loading secrets from the central repository
- `package.json` - Package configuration

## Usage

The `load-secrets.js` utility is used by agent skills to load secrets from the central repository instead of storing them in plugin.json files. See the [SECRETS.md](../SECRETS.md) file in the parent directory for more information.

```javascript
const loadSecrets = require('../utils/load-secrets');

// Get secrets for a specific skill
const skillId = 'your-skill-id';
const secrets = loadSecrets.getSecretsForSkill(skillId);

// Use secrets
const { YOUR_SECRET } = secrets;