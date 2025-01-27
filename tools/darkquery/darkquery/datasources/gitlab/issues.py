"""GitLab issue functionality."""
import gitlab
from typing import Dict, List, Optional

from ..base import DataSource, QueryResult
from .base import GitLabDataSource
from .projects import ProjectMixin


class IssuesMixin:
    """Mixin for GitLab issue operations."""

    def list_issues(self, params: Dict, limit: int = 5) -> QueryResult:
        """List issues based on parameters.
        
        Args:
            params: Query parameters
            limit: Maximum number of issues to return
            
        Returns:
            QueryResult containing issue list
        """
        try:
            # Get issues from group or globally
            if self.group:
                issues = self.group.issues.list(per_page=limit, **params)
            else:
                issues = self.client.issues.list(per_page=limit, **params)
            
            results = []
            for issue in issues:
                result = {
                    "id": issue.iid,
                    "title": issue.title,
                    "state": issue.state,
                    "type": "issue",
                    "web_url": issue.web_url,
                    "created_at": issue.created_at,
                    "updated_at": issue.updated_at
                }
                
                # Add details for single item view
                if limit == 1:
                    result.update({
                        "description": issue.description,
                        "author": issue.author['name'],
                        "assignees": [a['name'] for a in issue.assignees],
                        "labels": issue.labels
                    })
                    
                    # Get comments if available
                    if hasattr(issue, 'notes'):
                        result['comments'] = [{
                            "author": note.author['name'],
                            "body": note.body,
                            "created_at": note.created_at
                        } for note in issue.notes.list()]
                
                results.append(result)
            
            return QueryResult(
                success=True,
                data=results,
                metadata={"group": self.group.full_path if self.group else None}
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                message=f"Error listing issues: {str(e)}"
            )


# Add mixins to GitLab data source
class GitLabDataSourceWithIssues(IssuesMixin, ProjectMixin, GitLabDataSource):
    """GitLab data source with issue operations."""
    pass