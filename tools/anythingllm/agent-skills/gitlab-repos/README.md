# GitLab Repositories Agent Skill

This AnythingLLM agent skill lists repositories and projects from GitLab groups.

## Usage Examples

List repositories in a group:
```
List GitLab mangopay/appsec repos
Response:
Found 3 repositories in mangopay/appsec:
- security-tools (mangopay/appsec/security-tools)
  Security testing and scanning tools
  URL: https://gitlab.com/mangopay/appsec/security-tools

- vulnerability-reports (mangopay/appsec/vulnerability-reports)
  Security vulnerability tracking
  URL: https://gitlab.com/mangopay/appsec/vulnerability-reports

- security-policies (mangopay/appsec/security-policies)
  Security policies and procedures
  URL: https://gitlab.com/mangopay/appsec/security-policies
```

View a specific project:
```
Show GitLab repos in mangopay/appsec/security-tools
Response:
Found project mangopay/appsec/security-tools:
- Security Tools (mangopay/appsec/security-tools)
  Security testing and scanning tools
  URL: https://gitlab.com/mangopay/appsec/security-tools
```

## Required Fields

- `path`: GitLab group or project path (e.g., mangopay/appsec)

## Configuration

The skill requires the following credentials in the agent skills settings:

- `GITLAB_HOST`: Your GitLab instance URL (e.g., https://gitlab.com)
- `GITLAB_TOKEN`: Your GitLab private token (create at GitLab > Settings > Access Tokens)

## Dependencies

- axios: For making HTTP requests to GitLab API