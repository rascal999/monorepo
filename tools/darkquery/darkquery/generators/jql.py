"""JQL query handling for model-generated queries."""
from typing import Any, Dict, Optional


class JQLGenerator:
    """Handles JQL queries from model responses."""
    
    def validate_jql(self, jql: str) -> bool:
        """Validate if a JQL query is well-formed.
        
        Args:
            jql: JQL query string to validate
            
        Returns:
            bool indicating if query is valid
        """
        # Key lookups don't need ORDER BY
        if jql.strip().startswith('key ='):
            return True
            
        # Other queries should have ORDER BY
        if 'ORDER BY' not in jql:
            return False
            
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
        # Just validate and return it
        if not self.validate_jql(query):
            raise ValueError("Invalid JQL query - missing ORDER BY clause")
        
        return query