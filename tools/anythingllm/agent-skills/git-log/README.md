# Git Log Agent Skill

This AnythingLLM agent skill fetches and displays git commit history from GitLab repositories.

## Usage Examples

Get recent commits:
```
Show git log for mangopay/appsec/security-tools
Response:
Last 10 commits in mangopay/appsec/security-tools:

[a1b2c3d] 2024-02-24 14:30:00 by John Doe
Update security scanning rules
Files: +156 -23

[e4f5g6h] 2024-02-23 16:45:00 by Jane Smith
Fix false positive in XSS detection
Files: +45 -12

[i7j8k9l] 2024-02-22 09:15:00 by Alex Johnson
Add new vulnerability patterns
Files: +234 -56
```

Specify number of commits:
```
Get last 5 commits from mangopay/appsec/security-tools
Response:
Last 5 commits in mangopay/appsec/security-tools:
[Shows 5 most recent commits with details...]
```

## Required Fields

- `path`: GitLab repository path (e.g., mangopay/appsec/security-tools)
- `limit`: (Optional) Number of commits to fetch (default: 10)

## Configuration

The skill requires the following credentials in the agent skills settings:

- `GITLAB_HOST`: Your GitLab instance URL (e.g., https://gitlab.com)
- `GITLAB_TOKEN`: Your GitLab private token (create at GitLab > Settings > Access Tokens)

## Features

- Fetches recent commit history from GitLab repositories
- Shows commit details including:
  - Commit ID
  - Author name
  - Timestamp
  - Commit message
  - File changes statistics
- Configurable number of commits to display
- Error handling for common issues

## Dependencies

- axios: For making HTTP requests to GitLab API