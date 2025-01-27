"""GitLab merge request functionality."""
import gitlab
from typing import Dict, List, Optional

from ..base import DataSource, QueryResult
from .base import GitLabDataSource
from .projects import ProjectMixin


class MergeRequestsMixin:
    """Mixin for GitLab merge request operations."""

    def list_merge_requests(self, params: Dict, limit: int = 5) -> QueryResult:
        """List merge requests based on parameters.
        
        Args:
            params: Query parameters
            limit: Maximum number of merge requests to return
            
        Returns:
            QueryResult containing merge request list
        """
        try:
            # Get merge requests from group or globally
            if self.group:
                mrs = self.group.mergerequests.list(per_page=limit, **params)
            else:
                mrs = self.client.mergerequests.list(per_page=limit, **params)
            
            results = []
            for mr in mrs:
                result = {
                    "id": mr.iid,
                    "title": mr.title,
                    "state": mr.state,
                    "type": "merge_request",
                    "web_url": mr.web_url,
                    "created_at": mr.created_at,
                    "updated_at": mr.updated_at
                }
                
                # Add details for single item view
                if limit == 1:
                    result.update({
                        "description": mr.description,
                        "author": mr.author['name'],
                        "assignees": [a['name'] for a in mr.assignees],
                        "labels": mr.labels,
                        "source_branch": mr.source_branch,
                        "target_branch": mr.target_branch,
                        "merge_status": mr.merge_status
                    })
                    
                    # Get comments if available
                    if hasattr(mr, 'notes'):
                        result['comments'] = [{
                            "author": note.author['name'],
                            "body": note.body,
                            "created_at": note.created_at
                        } for note in mr.notes.list()]
                
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
                message=f"Error listing merge requests: {str(e)}"
            )


# Add mixins to GitLab data source
class GitLabDataSourceWithMergeRequests(MergeRequestsMixin, ProjectMixin, GitLabDataSource):
    """GitLab data source with merge request operations."""
    pass