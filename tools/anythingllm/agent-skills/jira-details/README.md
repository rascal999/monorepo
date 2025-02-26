# Jira Get Details Agent Skill

This AnythingLLM agent skill fetches details and comments from Jira tickets.

## Usage Examples

Get basic ticket details:
```
Get details of SECOPS-1234

I've successfully retrieved the Jira ticket SECOPS-1234. Here are the key details:

Title: Login page not responding
Status: In Progress
Priority: P1 - Critical
Type: Bug

Key Details:

    Reporter: John Doe
    Assignee: Jane Smith
    Created: February 24, 2025, 12:00:00 PM
    Last Updated: February 24, 2025, 12:30:00 PM

Description: Users cannot access the login page after recent deployment

View ticket: https://mangopay.atlassian.net/browse/SECOPS-1234
```

Get ticket details with comments:
```
Show me SECOPS-1234 with comments

I've successfully retrieved the Jira ticket SECOPS-1234. Here are the key details:

Title: Login page not responding
Status: In Progress
Priority: P1 - Critical
Type: Bug

Key Details:

    Reporter: John Doe
    Assignee: Jane Smith
    Created: February 24, 2025, 12:00:00 PM
    Last Updated: February 24, 2025, 12:30:00 PM

Description: Users cannot access the login page after recent deployment

Comments:

    John Doe (February 24, 2025, 12:15:00 PM):
    Initial investigation shows the issue might be related to the recent deployment.

    Jane Smith (February 24, 2025, 12:30:00 PM):
    Found the root cause. Working on a fix.

View ticket: https://mangopay.atlassian.net/browse/SECOPS-1234
```

## Required Fields

- `ticket`: Jira ticket key (e.g., SECOPS-1234)

## Optional Fields

- `includeComments`: Whether to include ticket comments (default: false)

## Configuration

The skill requires the following credentials in the agent skills settings:

- `JIRA_HOST`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_API_TOKEN`: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)

## Dependencies

- jira-client: ^8.2.2 (bundled with the skill)