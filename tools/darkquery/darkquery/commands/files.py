"""File command handling functionality."""
import json
import logging
from typing import Dict, Optional

from ..display import display_error, display_file_result


class FilesMixin:
    """Mixin for file command operations."""

    def _execute_files_command(self, command: Dict) -> Optional[None]:
        """Execute a files command.
        
        Args:
            command: Command dictionary to execute
        """
        if 'files' not in self.data_sources:
            display_error("File data source not configured")
            return
            
        cmd = command.get('command')
        params = command.get('params', {})
        
        logging.debug(f"Executing files command: cmd={cmd}, params={json.dumps(params)}")
        
        if cmd == 'read':
            path = params.get('path')
            if not path:
                display_error("Missing file path")
                return
                
            command = {
                "type": "read_file",
                "path": path
            }
            result = self.data_sources['files'].query(command)
            if result.success:
                display_file_result(result)
            else:
                display_error(result.message)
                
        else:
            display_error(f"Unknown file command: {cmd}")