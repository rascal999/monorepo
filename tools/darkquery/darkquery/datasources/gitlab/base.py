"""Base GitLab data source implementation."""
import logging
from typing import Any, Dict, List, Optional

import gitlab
from ..base import DataSource


class GitLabDataSource(DataSource):
    """GitLab data source implementation."""
    
    DEFAULT_LIMIT = 5  # Default number of results to return
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """Initialize GitLab data source.
        
        Args:
            config: Optional configuration dictionary containing:
                   - url: GitLab instance URL
                   - token: GitLab personal access token
                   - group: Optional default group/namespace to search in
        """
        self.config = config or {}
        self.logger = logging.getLogger("darkquery.gitlab")
        
        # Initialize GitLab client
        self.client = gitlab.Gitlab(
            url=self.config['url'],
            private_token=self.config['token']
        )
        
        # Store default group if provided
        self.default_group = self.config.get('group')
        if self.default_group:
            try:
                self.group = self.client.groups.get(self.default_group)
                self.logger.info(f"Using default group: {self.default_group}")
            except Exception as e:
                self.logger.warning(f"Failed to get default group: {str(e)}")
                self.group = None
        else:
            self.group = None
    
    def get_capabilities(self) -> List[str]:
        """Get list of supported GitLab query capabilities.
        
        Returns:
            List of capability strings
        """
        return [
            "issue_search",
            "issue_details",
            "issue_comments",
            "merge_request_search",
            "merge_request_details",
            "merge_request_comments",
            "project_search",
            "milestone_search"
        ]
    
    def get_schema(self) -> Dict[str, Any]:
        """Get GitLab schema information.
        
        Returns:
            Dict containing schema information
        """
        return {
            "issue_fields": {
                "id": "integer",
                "title": "string",
                "description": "string",
                "state": "string",
                "author": "string",
                "assignees": "list[string]",
                "created_at": "datetime",
                "updated_at": "datetime",
                "labels": "list[string]",
                "milestone": "string",
                "due_date": "date",
                "time_stats": "dict",
                "comments": "list[comment]"
            },
            "merge_request_fields": {
                "id": "integer", 
                "title": "string",
                "description": "string",
                "state": "string",
                "author": "string",
                "assignees": "list[string]",
                "created_at": "datetime",
                "updated_at": "datetime",
                "labels": "list[string]",
                "milestone": "string",
                "source_branch": "string",
                "target_branch": "string",
                "merge_status": "string",
                "comments": "list[comment]"
            },
            "supported_queries": [
                "open issues",
                "closed merge requests",
                "issues created this week",
                "merge requests created today",
                "issues assigned to me",
                "merge requests with label bug",
                "issues in project {project_id}"
            ]
        }