"""Context management for maintaining conversation state and history."""
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ContextEntry:
    """Represents a single context entry."""
    id: str
    source: str  # Data source type (jira, files, etc)
    data: Dict[str, Any]  # Context-specific data
    timestamp: float = field(default_factory=time.time)
    parent_id: Optional[str] = None  # For linking related contexts
    references: List[str] = field(default_factory=list)  # Referenced items (tickets, files)


class Context:
    """Manages conversation context and history."""
    
    def __init__(self, max_history: int = 50):
        """Initialize context manager.
        
        Args:
            max_history: Maximum number of context entries to maintain
        """
        self._contexts: List[ContextEntry] = []
        self._max_history = max_history
        self._active_context_id: Optional[str] = None
    
    def create_context(self, 
                      source: str, 
                      data: Dict[str, Any],
                      parent_id: Optional[str] = None) -> str:
        """Create a new context entry.
        
        Args:
            source: Data source type
            data: Context-specific data
            parent_id: Optional ID of parent context
            
        Returns:
            ID of created context
        """
        context_id = str(uuid.uuid4())
        entry = ContextEntry(
            id=context_id,
            source=source,
            data=data,
            parent_id=parent_id
        )
        
        self._contexts.append(entry)
        self._trim_history()
        self._active_context_id = context_id
        
        return context_id
    
    def add_reference(self, context_id: str, reference: str) -> None:
        """Add a reference to a context entry.
        
        Args:
            context_id: ID of context to update
            reference: Reference to add (ticket ID, file path, etc)
        """
        context = self.get_context(context_id)
        if context and reference not in context.references:
            context.references.append(reference)
    
    def get_context(self, context_id: str) -> Optional[ContextEntry]:
        """Get a specific context entry.
        
        Args:
            context_id: ID of context to retrieve
            
        Returns:
            ContextEntry if found, None otherwise
        """
        for context in self._contexts:
            if context.id == context_id:
                return context
        return None
    
    def get_active_context(self) -> Optional[Dict[str, Any]]:
        """Get currently active context data.
        
        Returns:
            Dict containing active context data if exists, None otherwise
        """
        if not self._active_context_id:
            return None
            
        context = self.get_context(self._active_context_id)
        if not context:
            return None
            
        return {
            "id": context.id,
            "source": context.source,
            "data": context.data,
            "references": context.references,
            "parent_id": context.parent_id
        }
    
    def has_active_context(self) -> bool:
        """Check if there is an active context.
        
        Returns:
            bool indicating if active context exists
        """
        return self._active_context_id is not None
    
    def clear_context(self) -> None:
        """Clear active context."""
        self._active_context_id = None
    
    def get_context_chain(self, context_id: str) -> List[ContextEntry]:
        """Get chain of related contexts.
        
        Args:
            context_id: Starting context ID
            
        Returns:
            List of related contexts from oldest to newest
        """
        chain = []
        current_id = context_id
        
        while current_id:
            context = self.get_context(current_id)
            if not context or context in chain:  # Prevent cycles
                break
            chain.append(context)
            current_id = context.parent_id
            
        return list(reversed(chain))  # Oldest to newest
    
    def _trim_history(self) -> None:
        """Trim context history to max size."""
        if len(self._contexts) > self._max_history:
            # Keep most recent contexts
            self._contexts = self._contexts[-self._max_history:]