"""GitLab command handling functionality."""
import json
import logging
from typing import Dict, Optional

from ..display import display_error, display_gitlab_result


class GitLabMixin:
    """Mixin for GitLab command operations."""

    def _execute_gitlab_command(self, command: Dict) -> Optional[None]:
        """Execute a GitLab command.
        
        Args:
            command: Command dictionary to execute
        """
        if 'gitlab' not in self.data_sources:
            display_error("GitLab data source not configured")
            return False
            
        cmd = command.get('command')
        params = command.get('params', {})
        
        logging.debug(f"Executing GitLab command: cmd={cmd}, params={json.dumps(params)}")
        
        if cmd == 'list_repos':
            project_id = params.get('project_id')
            limit = params.get('limit', 5)
            if not project_id:
                display_error("Missing project ID")
                return False
                
            command = {
                "type": "gitlab",
                "query": f"project={project_id}",
                "context": {"scope": "projects", "limit": limit}
            }
            self._execute_gitlab_query(command)
            return None
            
        elif cmd == 'list_files':
            project = params.get('project')
            path = params.get('path', '/')
            if not project:
                display_error("Missing project")
                return False
                
            command = {
                "type": "gitlab",
                "query": f"project={project}",
                "context": {"scope": "files", "path": path}
            }
            self._execute_gitlab_query(command)
            return None
            
        elif cmd == 'read_file':
            project = params.get('project')
            path = params.get('path')
            ref = params.get('ref')
            
            logging.debug(f"GitLab read_file params: project={project}, path={path}, ref={ref}")
            
            if not project or not path:
                display_error("Missing project or path")
                return False
            
            # Build command context
            context = {
                "scope": "file_content",
                "path": path,
                "ref": ref  # Always include ref from params
            }
            
            # Only merge with stored context if it's a GitLab context
            if hasattr(self, 'context') and self.context.get('type') == 'gitlab':
                stored_context = dict(self.context)
                context = {**stored_context, **context}  # Let command context override stored
            
            logging.debug(f"Final GitLab context: {json.dumps(context)}")
            
            command = {
                "type": "gitlab",
                "query": f"project={project}",
                "context": context
            }
            
            self._execute_gitlab_query(command)
            return None  # Command fully handled
            
        else:
            display_error(f"Unknown GitLab command: {cmd}")
            
    def _execute_gitlab_query(self, command: Dict) -> None:
        """Execute a GitLab query command.
        
        Args:
            command: Command dictionary to execute
        """
        if self.verbose:
            self.logger.info(f"Generated command: {json.dumps(command)}")
            
        result = self.data_sources['gitlab'].query(command['query'], command.get('context'))
        if result.success:
            # Update last viewed if it's a single item query
            if command.get('context', {}).get('limit', 5) == 1:
                item_type = command.get('context', {}).get('scope', 'issue')
                item_id = command['query']
                self.last_viewed = f"gitlab:{item_type}:{item_id}"
            display_gitlab_result(result)
        else:
            display_error(result.message)