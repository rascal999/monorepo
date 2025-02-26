# Jira Update Description Agent Skill

This AnythingLLM agent skill updates descriptions of existing Jira tickets.

## Usage Examples

Update ticket description:
```
Update description of SECOPS-1234 to: Users cannot access the login page after recent deployment
Response:
Successfully updated Jira ticket description!
Ticket: SECOPS-1234
URL: https://mangopay.atlassian.net/browse/SECOPS-1234

The description has been updated with your specified text. No further action is needed.
```

Set new description:
```
Set SECOPS-1234 description to: Need to implement two-factor authentication for admin users
Response:
Successfully updated Jira ticket description!
Ticket: SECOPS-1234
URL: https://mangopay.atlassian.net/browse/SECOPS-1234

The description has been updated with your specified text. No further action is needed.
```

## Required Fields

- `ticket`: Jira ticket key (e.g., SECOPS-1234)
- `description`: New description text for the ticket

## Configuration

The skill requires the following credentials in the agent skills settings:

- `JIRA_HOST`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_API_TOKEN`: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)

## Dependencies

- jira-client: ^8.2.2 (bundled with the skill)