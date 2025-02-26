# Jira Add Comment Agent Skill

This AnythingLLM agent skill adds comments to existing Jira tickets.

## Usage Examples

Add a comment:
```
Add comment to SECOPS-1234: Fixed the login issue
Response:
Successfully added comment to Jira ticket!
Ticket: SECOPS-1234
URL: https://mangopay.atlassian.net/browse/SECOPS-1234

The comment has been added to the ticket. No further action is needed.
```

Add test results:
```
Comment on SECOPS-1234: Testing completed, all tests passing
Response:
Successfully added comment to Jira ticket!
Ticket: SECOPS-1234
URL: https://mangopay.atlassian.net/browse/SECOPS-1234

The comment has been added to the ticket. No further action is needed.
```

## Required Fields

- `ticket`: Jira ticket key (e.g., SECOPS-1234)
- `comment`: Text to add as a comment

## Configuration

The skill requires the following credentials in the agent skills settings:

- `JIRA_HOST`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_API_TOKEN`: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)

## Dependencies

- jira-client: ^8.2.2 (bundled with the skill)