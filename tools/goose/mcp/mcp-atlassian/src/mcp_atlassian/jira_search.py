from typing import List, Optional

from .jira_client import JiraClient, logger
from .jira_issues import JiraIssues
from .types import Document

class JiraSearch(JiraClient):
    """Handles Jira search operations."""

    def __init__(self):
        super().__init__()
        self.issues = JiraIssues()

    def search_issues(
        self, jql: str, fields: str = "*all", start: int = 0, limit: int = 50, expand: Optional[str] = None
    ) -> List[Document]:
        """
        Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: Comma-separated string of fields to return
            start: Starting index
            limit: Maximum results to return
            expand: Fields to expand

        Returns:
            List of Documents containing matching issues
        """
        try:
            results = self.jira.jql(jql, fields=fields, start=start, limit=limit, expand=expand)

            documents = []
            for issue in results["issues"]:
                try:
                    # Get full issue details
                    doc = self.issues.get_issue(issue["key"], expand=expand)
                    documents.append(doc)
                except Exception as e:
                    logger.error(f"Error processing issue {issue['key']}: {str(e)}")
                    continue

            return documents

        except Exception as e:
            logger.error(f"Error searching issues with JQL {jql}: {str(e)}")
            raise

    def get_project_issues(self, project_key: str, start: int = 0, limit: int = 50) -> List[Document]:
        """
        Get all issues for a project.

        Args:
            project_key: The project key
            start: Starting index
            limit: Maximum results to return

        Returns:
            List of Documents containing project issues
        """
        jql = f"project = {project_key} ORDER BY created DESC"
        return self.search_issues(jql, start=start, limit=limit)