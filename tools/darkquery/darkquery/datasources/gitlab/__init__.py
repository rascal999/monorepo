"""GitLab data source package."""
import logging
from typing import Any, Dict, List, Optional

from ..base import DataSource, QueryResult
from .base import GitLabDataSource
from .projects import ProjectMixin
from .files import FilesMixin
from .issues import IssuesMixin
from .merge_requests import MergeRequestsMixin


class CompleteGitLabDataSource(
    FilesMixin,
    IssuesMixin,
    MergeRequestsMixin,
    ProjectMixin,
    GitLabDataSource
):
    """Complete GitLab data source with all functionality."""

    def validate_query(self, query: str) -> bool:
        """Validate if a query can be processed for GitLab.
        
        Args:
            query: Query string to validate
            
        Returns:
            bool indicating if query is valid
        """
        # All queries are considered valid since we handle different formats
        return bool(query and query.strip())

    def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a query against GitLab.
        
        Args:
            query: Query string
            context: Optional context information
            
        Returns:
            QueryResult containing the query results
        """
        try:
            # Handle file operations
            if context and context.get('scope') in ('files', 'file_content'):
                # Extract project name from query
                project_name = query.split('=')[1]
                path = context.get('path', '/')
                
                # Use last viewed project if placeholder is used
                if project_name == '<last_viewed_project>' and context.get('last_viewed_project'):
                    project_name = context['last_viewed_project']
                    self.logger.info(f"Using last viewed project: {project_name}")
                
                result = None
                if context.get('scope') == 'file_content':
                    result = self.get_file_content(project_name, path)
                else:
                    result = self.list_repository_files(project_name, path)
                
                # Store project path in context if operation succeeded
                if result and result.success and result.metadata and 'project' in result.metadata:
                    context['last_viewed_project'] = result.metadata['project']
                    self.logger.info(f"Stored project in context: {result.metadata['project']}")
                
                return result

            # Handle project listing queries
            if context and context.get('scope') == 'projects' and '/*' in query:
                # Extract group name from query (e.g., "project=appsec/*" -> "appsec")
                group_name = query.split('=')[1].replace('/*', '')
                result = self.list_group_projects(group_name)
                if result.success:
                    # Store project paths in context for subsequent operations
                    self.logger.info(f"Found {len(result.data)} projects in group {group_name}")
                    for project in result.data:
                        self.logger.info(f"Project path: {project['path']}")
                return result

            # Handle issues and merge requests
            limit = context.get('limit', self.DEFAULT_LIMIT) if context else self.DEFAULT_LIMIT
            
            if context and context.get('scope') == 'merge_requests':
                return self.list_merge_requests(params={}, limit=limit)
            elif context and context.get('scope') == 'issues':
                return self.list_issues(params={}, limit=limit)
            else:
                # Get both issues and merge requests
                issues = self.list_issues(params={}, limit=limit)
                mrs = self.list_merge_requests(params={}, limit=limit)
                
                if not issues.success and not mrs.success:
                    return QueryResult(
                        success=False,
                        data=None,
                        message="Error fetching issues and merge requests"
                    )
                
                # Combine results
                results = []
                if issues.success:
                    results.extend(issues.data)
                if mrs.success:
                    results.extend(mrs.data)
                    
                return QueryResult(
                    success=True,
                    data=results,
                    metadata={"group": self.group.full_path if self.group else None}
                )

        except Exception as e:
            self.logger.exception("Error executing GitLab query")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error executing query: {str(e)}"
            )