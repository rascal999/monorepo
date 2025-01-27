"""GitLab project listing functionality."""
import gitlab
from typing import Any, Dict, List, Optional

from ..base import DataSource, QueryResult
from .base import GitLabDataSource


class ProjectMixin:
    """Mixin for GitLab project operations."""

    def list_group_projects(self, group_name: str) -> QueryResult:
        """List projects in a group.
        
        Args:
            group_name: Name or path of the group
            
        Returns:
            QueryResult containing project list
        """
        try:
            # Search for group by name or path
            groups = self.client.groups.list(search=group_name)
            if not groups:
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"No group found matching '{group_name}'"
                )
            
            # Use first matching group
            group = groups[0]
            self.logger.info(f"Found group: {group.full_path} (ID: {group.id})")
            
            # Get all projects in group
            projects = group.projects.list(all=True)
            return QueryResult(
                success=True,
                data=[{
                    "name": project.name,
                    "path": project.path_with_namespace,
                    "description": project.description,
                    "web_url": project.web_url,
                    "last_activity": project.last_activity_at
                } for project in projects],
                metadata={"group": group_name}
            )
            
        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"Group '{group_name}' not found. Try using the full group path (e.g., org/group)"
                )
            return QueryResult(
                success=False,
                data=None,
                message=f"Error accessing group {group_name}: {str(e)}"
            )
        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                message=f"Error listing projects in group {group_name}: {str(e)}"
            )

    def get_project(self, project_name: str) -> Optional[Any]:
        """Get a project by name or path.
        
        Args:
            project_name: Name or path of the project
            
        Returns:
            Project object if found, None otherwise
        """
        try:
            try:
                # Try exact path first
                project = self.client.projects.get(project_name)
                self.logger.info(f"Found project by path: {project.path_with_namespace} (ID: {project.id})")
                return project
            except gitlab.exceptions.GitlabGetError:
                # Fall back to search
                projects = self.client.projects.list(search=project_name)
                if not projects:
                    return None
                
                # Use first matching project
                project = projects[0]
                self.logger.info(f"Found project by search: {project.path_with_namespace} (ID: {project.id})")
                return project
            
        except Exception as e:
            self.logger.error(f"Error getting project {project_name}: {str(e)}")
            return None


# Add mixin to GitLab data source
class GitLabDataSourceWithProjects(ProjectMixin, GitLabDataSource):
    """GitLab data source with project operations."""
    pass