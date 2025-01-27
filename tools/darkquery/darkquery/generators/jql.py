"""JQL query handling for model-generated queries."""
from typing import Any, Dict, Optional

import logging

class JQLGenerator:
    """Handles JQL queries from model responses."""
    
    def __init__(self):
        """Initialize JQL generator."""
        self.logger = logging.getLogger("darkquery.jql")
    """Handles JQL queries from model responses."""
    
    def validate_jql(self, jql: str) -> bool:
        """Validate if a JQL query is well-formed.
        
        Args:
            jql: JQL query string to validate
            
        Returns:
            bool indicating if query is valid
        """
        # Basic validation - ensure query is not empty
        jql = jql.strip()
        if not jql:
            return False
            
        # Key lookups and simple queries are valid
        if jql.startswith('key =') or jql.startswith('issue ='):
            return True
            
        # For complex queries, suggest ORDER BY but don't require it
        if 'ORDER BY' not in jql:
            self.logger.warning("Query missing ORDER BY clause - results may be inconsistent")
            
        return True
    
    def generate(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate JQL from query.
        
        Args:
            query: Query string
            context: Optional context information
            
        Returns:
            JQL query string
        """
        # The query should already be a JQL string from Ollama
        if not query.strip():
            raise ValueError("Empty JQL query")
            
        # Replace double quotes with single quotes to avoid JSON parsing issues
        query = query.replace('"', "'")
            
        # Add warning for missing ORDER BY but don't require it
        if 'ORDER BY' not in query:
            self.logger.warning("Query missing ORDER BY clause - results may be inconsistent")
        
        return query