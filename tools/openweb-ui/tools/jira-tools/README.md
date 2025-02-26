# Jira Tools

A collection of web UI tools for interacting with Jira instances.

## Tools

### 1. JQL Query Tool (jql.py)

Execute JQL queries and view results in a formatted table.

Features:
- Execute any JQL query
- View issue details (summary, status, assignee, priority, dates)
- Results displayed in markdown table format (up to 50 issues)
- Total count of matching issues
- Clickable ticket links
- Error handling and status updates

### 2. Ticket Content Tool (ticket_content.py)

Fetch detailed content of specific Jira tickets.

Features:
- Full ticket details including:
  - Summary and description
  - Status and priority
  - Assignee and reporter
  - Creation/update dates
  - Comments with author and timestamp
  - Attachments with download links
- Rendered markdown content
- Direct Jira link

### 3. Comments Tool (comments.py)

Fetch and display comments from Jira tickets.

Features:
- List all comments for a ticket
- Comment details including:
  - Author
  - Creation/update dates
  - Rendered content
- Markdown formatting
- Direct Jira link

### 4. Ticket Creation Tool (create_ticket.py)

Create new Jira tickets with user confirmation.

Features:
- Two-step creation process:
  1. Preview ticket details
  2. Create after confirmation
- Support for:
  - Summary and description
  - Issue type selection
  - Priority setting
- Markdown description formatting
- Direct link to created ticket
- Error handling and validation

## Configuration

All tools use the same valve configuration:

### Required Valves

- `jira_username`: Your Jira account email/username
- `jira_api_token`: Your Jira API token (generate from Atlassian account settings)
- `jira_project`: Default project key (required for ticket creation)

### Optional Valves

- `jira_url`: Your Jira instance URL (defaults to https://mangopay.atlassian.net)

## Example Usage

### JQL Query Tool
```python
# Search for SECOPS tickets
query = "project = SECOPS ORDER BY created DESC"

# Search for high priority issues
query = "priority = High AND status = Open ORDER BY created DESC"
```

### Ticket Content Tool
```python
# Fetch full ticket details
ticket_key = "PROJ-123"
```

### Comments Tool
```python
# Fetch all comments from a ticket
ticket_key = "PROJ-123"
```

### Ticket Creation Tool
```python
# Create a new task
summary = "Investigate security alert"
description = """
## Background
Security alert detected in production environment.

## Required Actions
1. Review logs
2. Analyze impact
3. Document findings
"""
issue_type = "Task"
priority = "High"

# First call shows preview and requests confirmation
# Second call (with confirmed=True) creates the ticket
```

## Dependencies

- aiohttp>=3.8.0
- pydantic>=2.0.0