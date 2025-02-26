# Jira Search Agent Skill

This AnythingLLM agent skill enables searching Jira issues using JQL (Jira Query Language).

## Setup

1. Place the skill directory in your AnythingLLM agent skills directory
2. Configure the following credentials in the agent skills settings:
   - `JIRA_HOST`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
   - `JIRA_EMAIL`: Your Jira account email
   - `JIRA_API_TOKEN`: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)

## Usage

Use the `@agent` command followed by your search query. The agent will interpret your request and convert it to JQL.

Examples:

```
@agent Find all high priority bugs in the PROJ project
@agent Show me open tasks assigned to me
@agent Find issues created in the last week
```

## JQL Examples

The skill supports any valid JQL query. Here are some common examples:

- `project = PROJ AND issuetype = Bug AND priority = High`
- `assignee = currentUser() AND status = Open`
- `created >= -1w`
- `project = PROJ AND status != Done ORDER BY priority DESC`
- `project in (PROJ1, PROJ2) AND labels = frontend`

## Dependencies

The following dependencies are bundled with the skill:
- jira-client: ^8.2.2 (Jira API client for Node.js)

## Error Handling

The skill will return appropriate error messages for:
- Missing credentials
- Invalid JQL syntax
- API connection issues
- No results found

## Security Note

Your Jira credentials are stored securely in AnythingLLM's configuration. Never share your API token or include it in any code repositories.