"""Command execution functionality."""
import json
import logging
from typing import Dict, Optional

from ..display import display_error
from .files import FilesMixin
from .gitlab import GitLabMixin
from .jira import JIRAMixin


class ExecuteMixin(GitLabMixin, JIRAMixin, FilesMixin):
    """Mixin for command execution operations."""

    def _execute_command(self, command: Dict) -> Optional[None]:
        """Execute a command from Ollama.
        
        Args:
            command: Command dictionary to execute
        """
        command_type = command.get('type')
        cmd = command.get('command')
        params = command.get('params', {})
        
        logging.debug(f"Executing command: type={command_type}, cmd={cmd}, params={json.dumps(params)}")
        
        if command_type == 'set_context':
            context_data = command.get('context', {})
            if not context_data:
                display_error("Missing context data")
                return
                
            source = context_data.get('type')
            if not source:
                display_error("Missing context type")
                return
                
            # Store context and return success
            self.context = context_data
            return None
            
        elif command_type == 'jql':
            self._execute_jql_command(command)
            
        elif command_type == 'jira':
            self._execute_jira_command(command)
            
        elif command_type == 'gitlab':
            self._execute_gitlab_command(command)
            
        elif command_type == 'files':
            self._execute_files_command(command)
            
        else:
            display_error(f"Unknown command type: {command_type}")