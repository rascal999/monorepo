# Slack Channel Reader Agent Skill

This AnythingLLM agent skill reads messages from Slack channels using natural language commands.

## Usage Examples

Get channel messages:
```
Show me messages from #security channel
Response:
Here are the last 50 messages from #security:

[2024-02-24 14:30:00] John Doe:
  New security patch released for API gateway
  (2 replies in thread)
  Reactions: +1: 3, eyes: 2

[2024-02-24 14:31:15] Jane Smith:
  Deploying to staging for testing
  Reactions: rocket: 1

[2024-02-24 14:32:00] Alex Johnson:
  All tests passing, ready for production
```

Different ways to request messages:
```
Get last messages from #general
Read messages from #team-updates
```

## Required Fields

- `channel`: Slack channel name without # prefix (e.g., 'security')

## Configuration

The skill requires the following credentials in the agent skills settings:

- `SLACK_TOKEN`: Your Slack User OAuth Token (starts with xoxp-)
  - Get it from https://api.slack.com/apps > Your App > OAuth & Permissions
  - Required scopes:
    - channels:history
    - channels:read
    - users:read

## Features

- Natural language commands to read channel messages
- Shows message details including:
  - Timestamp
  - Author's real name
  - Message content
  - Thread information
  - Reactions
- Channel ID caching:
  - Caches channel name to ID mappings
  - Cache refreshes after 30 days
  - Reduces API calls and improves performance
  - Stores channel ID, name, privacy status, and update time
- Proper error handling for:
  - Channel not found
  - Authentication issues
  - API rate limits
  - Network errors

## Testing

The agent includes two types of tests:

### Unit Tests
Run with:
```bash
npm install
npm test
```

Tests cover:
- Successful message fetching
- Channel not found handling
- Authentication errors
- Missing parameters
- Empty channel handling

### Live Tests
Run with:
```bash
npm install
npm run test:live
```

Live tests:
- Use actual Slack token from plugin.json
- Test real channel interactions
- Create/update channel cache
- Show available channels
- Test message fetching

## Dependencies

- @slack/web-api: Official Slack Web API client
- jest: Testing framework (dev dependency)