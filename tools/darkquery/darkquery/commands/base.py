"""Base command handler implementation."""
import json
import logging
import re
from typing import Dict, Optional

from ..display import (
    display_error,
    display_warning,
    display_jira_result,
    display_file_result,
    display_gitlab_result,
    console
)


class CommandHandler:
    """Handles command execution and processing."""
    
    def __init__(self, data_sources: Dict, ollama_client, verbose: bool = False):
        """Initialize command handler.
        
        Args:
            data_sources: Dictionary of available data sources
            ollama_client: Ollama client instance
            verbose: Enable verbose output
        """
        self.data_sources = data_sources
        self.ollama = ollama_client
        self.verbose = verbose
        self.logger = logging.getLogger("darkquery")
        self.last_viewed = None  # Track last viewed item
        self.context = {}  # Store context data
        self.ticket_summaries = {}  # Cache for ticket summaries
        
        # Get JIRA and GitLab URLs from config if available
        self.jira_url = None
        self.gitlab_url = None
        if 'jira' in data_sources:
            self.jira_url = data_sources['jira'].config.get('url')
        if 'gitlab' in data_sources:
            self.gitlab_url = data_sources['gitlab'].config.get('url')

    def build_context(self) -> Dict:
        """Build context dictionary for Ollama.
        
        Returns:
            Dict containing context information
        """
        # Start with stored context
        context = self.context.copy()
        
        # Add basic info
        context.update({
            "last_viewed": self.last_viewed,
            "data_sources": list(self.data_sources.keys())
        })
        
        # Add ticket/project metadata if available
        if self.last_viewed and self.last_viewed.startswith("gitlab:"):
            _, item_type, item_id = self.last_viewed.split(":")
            context["type"] = "gitlab"
            context["item_type"] = item_type
            context["item_id"] = item_id
        elif self.last_viewed and re.match(r'^[A-Z]+-\d+$', self.last_viewed):
            context["type"] = "jira"
            context["ticket"] = self.last_viewed
            
        return context

    def update_context(self, new_context: Dict) -> None:
        """Update stored context with new data.
        
        Args:
            new_context: New context data to store
        """
        self.context.update(new_context)

    def process_query(self, query: str) -> None:
        """Process a query through Ollama.
        
        Args:
            query: Query string to process
        """
        try:
            query = query.strip()
            
            # Handle empty input - show cached summary if in ticket context
            if not query:
                if self.context.get('type') == 'jira' and self.context.get('ticket'):
                    ticket_id = self.context['ticket']
                    if ticket_id in self.ticket_summaries:
                        console.print(self.ticket_summaries[ticket_id])
                        return
                return
                
            # Handle special commands
            if query.lower() == 'context':
                self.handle_context()
                return

            # Check if query is a ticket ID or GitLab item
            ticket_match = re.match(r'^([A-Z]+-\d+)$', query)
            gitlab_issue_match = re.match(r'^#(\d+)$', query)
            gitlab_mr_match = re.match(r'^!(\d+)$', query)
            
            if ticket_match:
                ticket_id = ticket_match.group(1)
                if ticket_id in self.ticket_summaries:
                    console.print(self.ticket_summaries[ticket_id])
                else:
                    self._handle_ticket_query(ticket_id)
                return
            elif gitlab_issue_match:
                self._handle_gitlab_query('issue', gitlab_issue_match.group(1))
                return
            elif gitlab_mr_match:
                self._handle_gitlab_query('merge_request', gitlab_mr_match.group(1))
                return
            
            # Get response from Ollama
            response = self.ollama.query(query, self.build_context())
            
            # Try to parse as JSON command(s)
            try:
                # Split response by newlines and parse each line as a command
                commands = []
                for line in response.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('<') or line.endswith('>'):
                        continue
                    try:
                        command = json.loads(line)
                        commands.append(command)
                    except:  # Catch any JSON parsing error
                        continue

                # Execute commands in sequence
                for i, command in enumerate(commands):
                    result = self._execute_command(command)
                    if result is False:  # Error occurred
                        continue
                    # Only return None if it's the last command and not set_context
                    if result is None and command.get('type') != 'set_context':
                        if i == len(commands) - 1:  # Last command
                            return None
            except Exception as e:
                # Not a JSON command, just display the response
                console.print(response)
            return response
                
        except Exception as e:
            self.logger.exception("Error processing query")
            display_error(str(e))

    def handle_context(self) -> None:
        """Handle the context command by displaying current context."""
        context = self.build_context()
        console.print(json.dumps(context, indent=2))