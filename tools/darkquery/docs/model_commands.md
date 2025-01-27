# Model Commands

This document lists all available model commands and their usage examples.

## JIRA Commands

Format: `{"type": "jira", "command": "command_name", "params": {...}}`

### Fetch Ticket
Gets details for a specific JIRA ticket.

```json
{
  "type": "jira",
  "command": "fetch_ticket",
  "params": {
    "ticket": "PROJ-123",
    "limit": 1
  }
}
```

### Add Comment
Adds a comment to a JIRA ticket.

```json
{
  "type": "jira",
  "command": "add_comment",
  "params": {
    "ticket": "PROJ-123",
    "message": "Your comment text"
  }
}
```

## GitLab Commands

Format: `{"type": "gitlab", "command": "command_name", "params": {...}}`

### List Files
Lists files in a repository.

```json
{
  "type": "gitlab",
  "command": "list_files",
  "params": {
    "project": "group/repo",
    "path": "/"
  }
}
```

### Read File
Reads contents of a file from repository.

```json
{
  "type": "gitlab",
  "command": "read_file",
  "params": {
    "project": "group/repo",
    "path": "src/file.js"
  }
}
```

### List Repositories
Lists repositories in a group/project.

```json
{
  "type": "gitlab",
  "command": "list_repos",
  "params": {
    "project_id": "group/*",
    "limit": 5
  }
}
```

### Get Issue
Gets details for a specific GitLab issue.

```json
{
  "type": "gitlab",
  "command": "get_issue",
  "params": {
    "project": "group/repo",
    "issue_id": "123"
  }
}
```

### List Merge Requests
Lists merge requests for a project.

```json
{
  "type": "gitlab",
  "command": "list_mrs",
  "params": {
    "project": "group/repo",
    "state": "opened",
    "limit": 5
  }
}
```

## File Commands

Format: `{"type": "files", "command": "command_name", "params": {...}}`

### Read File
Reads the contents of a file.

```json
{
  "type": "files",
  "command": "read",
  "params": {
    "path": "src/auth.js"
  }
}
```

### List Files
Lists files in a directory.

```json
{
  "type": "files",
  "command": "list",
  "params": {
    "path": "src",
    "recursive": true
  }
}
```

## Context Setting

When setting context for subsequent operations:

```json
{
  "set_context": {
    "type": "jira",
    "ticket": "PROJ-123",
    "summary": "Bug fix",
    "status": "Open",
    "assignee": "John Doe"
  }
}
```

```json
{
  "set_context": {
    "type": "gitlab",
    "project": "group/repo",
    "description": "Project description"
  }
}