# Jira Create Ticket Agent Skill

This AnythingLLM agent skill creates new Jira tickets.

## Usage Examples

Create a basic ticket:
```
Create test ticket in SECOPS
Response:
Successfully created Jira ticket!
Ticket: SECOPS-1234
URL: https://mangopay.atlassian.net/browse/SECOPS-1234

The ticket has been created with your specified details. No further action is needed.
```

Create a bug ticket:
```
Create bug ticket in SECOPS: Login page not responding
Response:
Successfully created Jira ticket!
Ticket: SECOPS-1235
URL: https://mangopay.atlassian.net/browse/SECOPS-1235

The ticket has been created with your specified details. No further action is needed.
```

## Required Fields

- `project`: Jira project key (e.g., SECOPS)
- `summary`: Issue title/summary

## Optional Fields

- `type`: Issue type (Bug, Task, Story, etc.). Defaults to "Task"
- `description`: Detailed description. Defaults to "No description provided"

## Configuration

The skill requires the following credentials in the agent skills settings:

- `JIRA_HOST`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_API_TOKEN`: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)

## Dependencies

- jira-client: ^8.2.2 (bundled with the skill)