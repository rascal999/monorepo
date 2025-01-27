"""GitLab file listing functionality."""
import gitlab
import json
import logging
from typing import Dict, List, Optional, Any

from ..base import DataSource, QueryResult
from .base import GitLabDataSource
from .projects import ProjectMixin


class FilesMixin:
    """Mixin for GitLab file operations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query_context = None

    def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a query, storing the context for file operations.
        
        Args:
            query: The query string to execute
            context: Optional context information for the query
        """
        logging.debug(f"GitLab FilesMixin query called with context: {json.dumps(context)}")
        # Store context for file operations
        self._query_context = context
        
        # Call parent query implementation
        return super().query(query, context)

    def list_repository_files(self, project_name: str, path: str = "/") -> QueryResult:
        """List files in a repository.
        
        Args:
            project_name: Name or path of the project
            path: Optional path within repository
            
        Returns:
            QueryResult containing file list
        """
        try:
            # Get project
            logging.debug(f"Getting project: {project_name}")
            project = self.get_project(project_name)
            if not project:
                logging.debug(f"No project found matching '{project_name}'")
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"No project found matching '{project_name}'"
                )
            
            # Get repository tree
            logging.debug(f"Getting repository tree for {project.path_with_namespace} at path: {path}")
            tree = project.repository_tree(path=path, recursive=True, all=True)
            
            return QueryResult(
                success=True,
                data=[{
                    "name": item['name'],
                    "path": item['path'],
                    "type": item['type']
                } for item in tree],
                metadata={"project": project.path_with_namespace, "path": path}
            )
            
        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                logging.debug(f"Project not found: {project_name}, response code: 404")
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"Project '{project_name}' not found. Try using the full project path (e.g., group/project)"
                )
            logging.error(f"GitLab error accessing project {project_name}: {str(e)}")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error accessing project {project_name}: {str(e)}"
            )
        except Exception as e:
            logging.error(f"Unexpected error listing files in project {project_name}: {str(e)}")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error listing files in project {project_name}: {str(e)}"
            )

    def get_file_content(self, project_name: str, file_path: str, ref: Optional[str] = None) -> QueryResult:
        """Get content of a file from repository.
        
        Args:
            project_name: Name or path of the project
            file_path: Path to file within repository
            ref: Optional git reference (branch, tag, commit)
            
        Returns:
            QueryResult containing file content
        """
        try:
            # Get project
            logging.debug(f"Getting project for file content: {project_name}")
            project = self.get_project(project_name)
            if not project:
                logging.debug(f"No project found matching '{project_name}'")
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"No project found matching '{project_name}'"
                )
            
            # Get file content
            # First try ref from params, then query context ref, then default to 'main'
            context_ref = self._query_context.get('ref') if self._query_context else None
            use_ref = ref or context_ref or 'main'
            logging.debug(f"Ref resolution: param_ref={ref}, context_ref={context_ref}, use_ref={use_ref}, query_context={json.dumps(self._query_context)}")
            
            try:
                logging.debug(f"Attempting to get file {file_path} with ref {use_ref}")
                file = project.files.get(file_path=file_path, ref=use_ref)
                content = file.decode().decode('utf-8')
                logging.debug(f"Successfully retrieved file content for {file_path}")
                
                return QueryResult(
                    success=True,
                    data=content,
                    metadata={
                        "project": project.path_with_namespace,
                        "path": file_path,
                        "ref": use_ref  # Return actual ref used
                    }
                )
            except gitlab.exceptions.GitlabGetError as e:
                logging.debug(f"GitLab error getting file {file_path}: {str(e)}, response code: {e.response_code}")
                if e.response_code == 404:
                    return QueryResult(
                        success=False,
                        data=None,
                        message=f"File '{file_path}' not found in project '{project_name}' at ref '{use_ref}'"
                    )
                raise  # Re-raise to be caught by outer exception handler
                
        except gitlab.exceptions.GitlabGetError as e:
            logging.error(f"GitLab error accessing file {file_path}: {str(e)}")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error accessing file {file_path}: {str(e)}"
            )
        except Exception as e:
            logging.error(f"Unexpected error getting file content from {project_name}/{file_path}: {str(e)}")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error getting file content from {project_name}/{file_path}: {str(e)}"
            )


# Add mixins to GitLab data source
class GitLabDataSourceWithFiles(FilesMixin, ProjectMixin, GitLabDataSource):
    """GitLab data source with file operations."""
    pass