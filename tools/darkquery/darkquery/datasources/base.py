"""Base interface for all data sources."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class QueryResult:
    """Represents a query result from any data source."""
    success: bool
    data: Any
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataSource(ABC):
    """Abstract base class for all data sources."""
    
    @abstractmethod
    def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a query against the data source.
        
        Args:
            query: The query string to execute
            context: Optional context information for the query
            
        Returns:
            QueryResult containing the query results
        """
        pass
    
    @abstractmethod
    def validate_query(self, query: str) -> bool:
        """Validate if a query is valid for this data source.
        
        Args:
            query: The query string to validate
            
        Returns:
            bool indicating if query is valid
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of supported query capabilities.
        
        Returns:
            List of capability strings
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get schema information for this data source.
        
        Returns:
            Dict containing schema information
        """
        pass

    def supports_capability(self, capability: str) -> bool:
        """Check if data source supports a specific capability.
        
        Args:
            capability: Capability string to check
            
        Returns:
            bool indicating if capability is supported
        """
        return capability in self.get_capabilities()