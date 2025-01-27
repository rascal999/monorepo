"""Command processor for handling both direct and natural language commands."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union

from .context import Context
from .datasources.base import DataSource, QueryResult


class CommandType(Enum):
    """Types of commands that can be processed."""
    DIRECT = auto()      # Direct commands like 'open_last'
    NATURAL = auto()     # Natural language queries
    FOLLOWUP = auto()    # Follow-up questions using context


@dataclass
class Command:
    """Represents a processed command."""
    type: CommandType
    action: str
    params: Dict[str, Any]
    source: Optional[str] = None  # Target data source if applicable
    context_id: Optional[str] = None  # For linking related commands


class CommandProcessor:
    """Processes both direct commands and natural language queries."""
    
    def __init__(self, data_sources: Dict[str, DataSource]):
        """Initialize with available data sources.
        
        Args:
            data_sources: Dictionary mapping source names to DataSource instances
        """
        self.data_sources = data_sources
        self.context = Context()
    
    def process(self, input_text: str) -> Union[Command, QueryResult]:
        """Process input text into a command or direct result.
        
        Args:
            input_text: The input text to process
            
        Returns:
            Either a Command object for further processing or
            a QueryResult for direct commands
        """
        # Handle direct commands first
        if self._is_direct_command(input_text):
            return self._handle_direct_command(input_text)
            
        # Check if this is a follow-up question
        if self.context.has_active_context():
            command = self._process_followup(input_text)
            if command:
                return command
        
        # Process as natural language query
        return self._process_natural_language(input_text)
    
    def _is_direct_command(self, text: str) -> bool:
        """Check if text is a direct command."""
        direct_commands = {
            'open_last',
            'exit',
            'help',
            # Add more direct commands here
        }
        return text.strip().lower() in direct_commands
    
    def _handle_direct_command(self, command: str) -> Command:
        """Handle a direct command."""
        return Command(
            type=CommandType.DIRECT,
            action=command.lower(),
            params={},
        )
    
    def _process_followup(self, text: str) -> Optional[Command]:
        """Process a potential follow-up question."""
        context = self.context.get_active_context()
        if not context:
            return None
            
        # Analyze if text is related to current context
        if self._is_related_to_context(text, context):
            return Command(
                type=CommandType.FOLLOWUP,
                action="query",
                params={"text": text},
                source=context.get("source"),
                context_id=context.get("id")
            )
        return None
    
    def _process_natural_language(self, text: str) -> Command:
        """Process natural language into a command."""
        # Determine most likely data source based on text
        source = self._determine_data_source(text)
        
        return Command(
            type=CommandType.NATURAL,
            action="query",
            params={"text": text},
            source=source
        )
    
    def _is_related_to_context(self, text: str, context: Dict[str, Any]) -> bool:
        """Check if text is related to current context."""
        # TODO: Implement more sophisticated context relation checking
        return True
    
    def _determine_data_source(self, text: str) -> str:
        """Determine most appropriate data source for query."""
        # Simple heuristic based on keywords
        if any(word in text.lower() for word in ['ticket', 'bug', 'issue', 'jira']):
            return 'jira'
        if any(word in text.lower() for word in ['file', 'code', 'read', 'implementation']):
            return 'files'
        # Default to jira if unclear
        return 'jira'
            
        # Check for JIRA keywords
        if any(word in text_lower for word in ['ticket', 'bug', 'jira']):
            return 'jira'
            
        # Check for file operations
        if any(word in text_lower for word in ['file', 'code', 'read', 'implementation']):
            return 'files'
            
        # Check if it's an issue (could be either JIRA or GitLab)
        if 'issue' in text_lower:
            # If mentions GitLab group/project, use GitLab
            if 'group' in text_lower or 'project' in text_lower:
                return 'gitlab'
            return 'jira'  # Default to JIRA for general issues
            
        # Default to JIRA if unclear
        return 'jira'