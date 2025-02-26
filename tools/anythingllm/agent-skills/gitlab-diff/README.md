# GitLab Diff Agent Skill

This AnythingLLM agent skill fetches and displays commit diffs from GitLab repositories.

## Usage Examples

View commit changes:
```
Show diff for commit a1b2c3d in mangopay/appsec/security-tools
Response:
Commit Details:
Hash: a1b2c3d
Author: John Doe
Date: 2024-02-24 14:30:00
Message: Update security scanning rules

Changes (2 files modified):

File: security/rules/xss.yml
Changes: +15 -3

-rules:
-  - id: old-xss-rule
-    severity: high
+rules:
+  - id: enhanced-xss-detection
+    severity: critical
+    description: Enhanced XSS pattern detection
+    patterns:
+      - pattern: '(?i)(<script|javascript:)'
+      - pattern: '(?i)(onload|onerror|onmouseover)'
+    mitigation: Implement proper input sanitization

File: docs/CHANGELOG.md
Changes: +3 -0

+## [1.2.0] - 2024-02-24
+
+- Enhanced XSS detection rules with additional patterns
```

Get specific commit changes:
```
Get changes from commit e4f5g6h in mangopay/appsec/security-tools
Response:
[Shows detailed commit information and changes...]
```

## Required Fields

- `path`: GitLab repository path (e.g., mangopay/appsec/security-tools)
- `hash`: Commit hash to fetch diff for

## Configuration

The skill requires the following credentials in the agent skills settings:

- `GITLAB_HOST`: Your GitLab instance URL (e.g., https://gitlab.com)
- `GITLAB_TOKEN`: Your GitLab private token (create at GitLab > Settings > Access Tokens)

## Features

- Fetches detailed commit information
- Shows file-by-file changes including:
  - Added and removed lines
  - File status (new, deleted, renamed)
  - Line-by-line diff with color coding
- Handles various diff scenarios:
  - Modified files
  - New files
  - Deleted files
  - Renamed files
- Provides commit metadata:
  - Author
  - Timestamp
  - Commit message
  - Change statistics

## Dependencies

- axios: For making HTTP requests to GitLab API