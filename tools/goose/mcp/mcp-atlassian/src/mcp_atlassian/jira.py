from .jira_client import JiraClient
from .jira_issues import JiraIssues
from .jira_links import JiraLinks
from .jira_search import JiraSearch

class JiraFetcher(JiraIssues, JiraLinks, JiraSearch):
    """
    Main Jira interface that combines all functionality:
    - Issue operations (create, read, update, comment)
    - Link operations (create, read, delete)
    - Search operations (JQL search, project issues)
    """
    pass  # All functionality is inherited from parent classes
