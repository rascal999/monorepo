# darkquery Examples

This document provides examples of using darkquery in interactive mode, which is the default and recommended way to use the tool.

## Basic Usage

Start the tool:
```bash
darkquery
```

## Querying Tickets

### Finding Recent Tickets
```
> Show my recent tickets
Generated JQL: {"type": "jql", "query": "assignee = currentUser() ORDER BY updated DESC LIMIT 5"}
Found tickets:
PROJ-123: Update user authentication (In Progress)
PROJ-124: Fix pagination bug (Open)
PROJ-125: Add dark mode support (In Review)

> Show tickets I created this week
Generated JQL: {"type": "jql", "query": "creator = currentUser() AND created >= startOfWeek() ORDER BY created DESC LIMIT 5"}
Found tickets:
PROJ-126: Implement search filters (Open)
PROJ-127: Update API documentation (Done)
```

### Searching by Status
```
> Show all open bugs
Generated JQL: {"type": "jql", "query": "type = Bug AND status = Open ORDER BY priority DESC LIMIT 5"}
Found tickets:
BUG-101: Search fails with special characters
BUG-102: Memory leak in background process
BUG-103: Mobile layout breaks on small screens

> Show critical bugs in progress
Generated JQL: {"type": "jql", "query": "type = Bug AND priority = Critical AND status = 'In Progress' ORDER BY created DESC LIMIT 5"}
Found tickets:
BUG-104: Production database timeout
BUG-105: Payment processing error
```

### Finding Assigned Tickets
```
> Show tickets assigned to Bob
Generated JQL: {"type": "jql", "query": "assignee = 'Bob Smith' ORDER BY updated DESC LIMIT 5"}
Found tickets:
PROJ-128: Code review feedback
PROJ-129: Performance optimization

> Show unassigned tickets in current sprint
Generated JQL: {"type": "jql", "query": "assignee = EMPTY AND sprint in openSprints() ORDER BY priority DESC LIMIT 5"}
Found tickets:
PROJ-130: Update test coverage
PROJ-131: Documentation review
```

## Working with a Ticket

### Viewing Details
```
> Show me BUG-101
Using concise summary prompt...

TL;DR: Search functionality breaks when users input special characters

Key Points:
• Search fails with SQL injection-like characters (', ", %)
• Affects both basic and advanced search features
• High priority issue affecting multiple users

Stakeholders:
• Sarah Chen (QA Lead) - Identified and documented reproduction steps
• Mike Johnson (Backend Dev) - Investigating SQL query sanitization

Possible Next Steps:
• Implement input sanitization in search API
• Add regression tests for special character handling

> What's the impact of this bug?
Based on the ticket context:
The bug affects all search functionality across the platform. When users include
special characters in their search queries (like apostrophes or quotes), the
search fails completely. This impacts both basic text search and advanced
filtering options. Multiple users have reported this issue, making it a high
priority fix.

> Who's working on it?
Based on the ticket context:
Mike Johnson from the backend team is currently investigating the issue,
focusing on SQL query sanitization. Sarah Chen from QA is providing support
with reproduction cases and testing scenarios.

> Show comments for BUG-101
[Sarah Chen] 2024-01-26:
Added reproduction steps:
1. Search for "O'Brien"
2. Search for "20% discount"
Both queries fail with SQL error

[Mike Johnson] 2024-01-27:
Found root cause - missing parameterized queries.
Will implement fix today.
```

### Navigation
```
> open_last
Opening PROJ-123 in browser...

> Show related tickets
Found tickets:
PROJ-120: Security requirements doc
PROJ-121: API authentication spec
PROJ-122: Frontend auth components
```

## Advanced Queries

### Complex Searches
```
> Show high priority tickets updated in the last 24 hours
Generated JQL: {"type": "jql", "query": "priority in (Critical, High) AND updated >= -24h ORDER BY priority DESC, updated DESC LIMIT 5"}
Found tickets:
PROJ-140: Data migration failing (Critical)
PROJ-141: API rate limiting issue (High)

> Show tickets blocked by PROJ-123
Generated JQL: {"type": "jql", "query": "'Blocked By' = PROJ-123 ORDER BY priority DESC LIMIT 5"}
Found tickets:
PROJ-150: Frontend authentication UI
PROJ-151: Mobile app authentication
```

### Sprint Management
```
> Show tickets in current sprint
Generated JQL: {"type": "jql", "query": "sprint in openSprints() ORDER BY status ASC, priority DESC LIMIT 5"}
Found tickets:
PROJ-160: Sprint planning (Done)
PROJ-161: Daily standup notes (In Progress)
PROJ-162: Retrospective prep (Open)

> Show incomplete tickets due this week
Generated JQL: {"type": "jql", "query": "status not in (Done, Closed) AND duedate <= endOfWeek() AND duedate >= startOfWeek() ORDER BY duedate ASC LIMIT 5"}
Found tickets:
PROJ-170: Release notes
PROJ-171: Deployment checklist
```

## Using Debug Mode

Start with debug enabled:
```bash
darkquery -v -d
```

Example debug output:
```
> Show my recent tickets
[DEBUG] Getting command context for query: Show my recent tickets
[DEBUG] Using JQL context for general query
[DEBUG] Detected command format
[DEBUG] Routing to JQL handler
Found tickets:
PROJ-180: Example ticket
PROJ-181: Another ticket
```

## Tips

1. Natural Language:
   - Use natural language queries instead of remembering specific commands
   - The tool will convert your query into appropriate commands

2. Context Awareness:
   - The tool remembers the last viewed ticket
   - References like "this ticket" or "related tickets" use this context

3. Command History:
   - Use Up/Down arrows to navigate previous commands
   - Commands are persisted across sessions

4. Tab Completion:
   - Use Tab to complete ticket IDs and commands
   - Works for file paths when using file data source

## Working with Files

### Reading Source Code
```
> Read src/auth.js
Generated Command: {"type": "read_file", "path": "src/auth.js"}
Reading file...
[Shows file content with syntax highlighting]

> Show me the implementation of login function
Generated Command: {"type": "read_file", "path": "src/auth.js"}
Reading file...
function login(username, password) {
    // Implementation details shown
}

> Find all API endpoints in this project
Generated Command: {"type": "read_file", "path": "src/api/endpoints.js"}
Reading files...
Found in src/api/endpoints.js:
- POST /api/auth/login
- GET /api/users
- PUT /api/settings
```

### Documentation and Config Files
```
> Show me the README
Generated Command: {"type": "read_file", "path": "README.md"}
Reading README.md...
[Shows formatted markdown content]

> What are the current environment variables?
Generated Command: {"type": "read_file", "path": ".env.example"}
Reading .env.example...
Available environment variables:
- API_URL: Base API URL
- DEBUG: Enable debug mode
- LOG_LEVEL: Logging verbosity

> Check package.json dependencies
Generated Command: {"type": "read_file", "path": "package.json"}
Reading package.json...
Dependencies:
- react: ^18.0.0
- express: ^4.17.1
- typescript: ^4.8.0
```

### Code Analysis
```
> Read src/auth.js
Generated Command: {"type": "read_file", "path": "src/auth.js"}
Reading file...
[Shows auth.js content including login function]

> What does this login function do?
Based on the file context:
The login function handles user authentication by:
1. Validating credentials against the database
2. Generating JWT tokens on success
3. Setting up refresh token rotation
4. Logging authentication attempts

> Are there any security concerns?
Based on the file context:
Several potential issues:
1. Password hashing not using latest bcrypt version
2. Token expiration too long (30 days)
3. Missing rate limiting on failed attempts
4. Refresh tokens stored in memory

> Show me all TODO comments in the project
Searching files...
Found TODOs:
src/auth.js:45: TODO: Add refresh token handling
src/api/users.js:78: TODO: Implement pagination
src/utils/logger.js:12: TODO: Add log rotation

> Which of these TODOs is most critical?
Based on the code context and previous security discussion:
The refresh token handling TODO in auth.js is most critical since it relates
to the security concerns we identified - particularly the in-memory token
storage and long expiration times. This should be prioritized to improve
the authentication security.