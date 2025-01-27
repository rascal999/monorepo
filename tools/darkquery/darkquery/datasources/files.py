"""File system data source implementation."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import TerminalFormatter

from .base import DataSource, QueryResult


class FileDataSource(DataSource):
    """File system data source implementation."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """Initialize file system data source.
        
        Args:
            config: Optional configuration dictionary containing:
                   - base_path: Base directory for file operations
                   - allowed_extensions: List of allowed file extensions
        """
        self.config = config or {}
        self.base_path = Path(self.config.get('base_path', '.'))
        self.logger = logging.getLogger("darkquery.files")
        
        # Default to common code and doc files if not specified
        self.allowed_extensions = self.config.get('allowed_extensions', [
            '.py', '.js', '.ts', '.java', '.cpp', '.h', '.c',
            '.md', '.txt', '.json', '.yaml', '.yml'
        ])
    
    def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a file-related query.
        
        Args:
            query: Query object from model
            context: Optional context information
            
        Returns:
            QueryResult containing the query results
        """
        try:
            # Expect query to be a dict from model with operation details
            if isinstance(query, str):
                return QueryResult(
                    success=False,
                    data=None,
                    message="Expected query object from model"
                )
                
            operation = query.get('type')
            if operation == 'read_file':
                return self._handle_read_file(query)
            elif operation == 'search_code':
                return self._handle_search_code(query)
            else:
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"Unsupported operation: {operation}"
                )
                
        except Exception as e:
            self.logger.exception("Error executing file query")
            return QueryResult(
                success=False,
                data=None,
                message=f"Error executing query: {str(e)}"
            )
    
    def _handle_read_file(self, query: Dict[str, Any]) -> QueryResult:
        """Handle file reading operation.
        
        Args:
            query: Query object containing file path
            
        Returns:
            QueryResult containing file contents
        """
        path = query.get('path')
        if not path:
            return QueryResult(
                success=False,
                data=None,
                message="No file path provided"
            )
            
        file_path = self.base_path / path
        
        if not file_path.exists():
            return QueryResult(
                success=False,
                data=None,
                message=f"File not found: {path}"
            )
            
        if file_path.suffix not in self.allowed_extensions:
            return QueryResult(
                success=False,
                data=None,
                message=f"File type not supported: {path}"
            )
            
        try:
            content = file_path.read_text()
            
            # Syntax highlight if it's a code file
            try:
                lexer = get_lexer_for_filename(path)
                highlighted = highlight(content, lexer, TerminalFormatter())
                content = highlighted
            except:
                # Fall back to plain text if highlighting fails
                pass
                
            return QueryResult(
                success=True,
                data=content,
                metadata={
                    "path": str(path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                }
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                message=f"Error reading file: {str(e)}"
            )
    
    def _handle_search_code(self, query: Dict[str, Any]) -> QueryResult:
        """Handle code search operation.
        
        Args:
            query: Query object containing search parameters
            
        Returns:
            QueryResult containing search results
        """
        # This would be implemented to handle code search queries
        # For now return not implemented
        return QueryResult(
            success=False,
            data=None,
            message="Code search not implemented yet"
        )
    
    def validate_query(self, query: str) -> bool:
        """Validate if a query can be processed for files.
        
        Args:
            query: Query string to validate
            
        Returns:
            bool indicating if query is valid
        """
        # File operations should come as structured queries from model
        return isinstance(query, dict) and 'type' in query
    
    def get_capabilities(self) -> List[str]:
        """Get list of supported file operation capabilities.
        
        Returns:
            List of capability strings
        """
        return [
            "read_file",
            "search_code",
            "list_files",
            "analyze_code"
        ]
    
    def get_schema(self) -> Dict[str, Any]:
        """Get file operations schema information.
        
        Returns:
            Dict containing schema information
        """
        return {
            "operations": {
                "read_file": {
                    "parameters": {
                        "path": "string"
                    }
                },
                "search_code": {
                    "parameters": {
                        "pattern": "string",
                        "file_types": "list[string]",
                        "max_results": "integer"
                    }
                }
            },
            "supported_extensions": self.allowed_extensions
        }