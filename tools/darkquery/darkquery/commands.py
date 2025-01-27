"""Command handling for darkquery."""
import json
import logging
import re
import webbrowser
from typing import Dict, Optional

from .display import display_error, display_warning, display_jira_result, display_file_result, console


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
        
        # Get JIRA URL from config if available
        self.jira_url = None
        if 'jira' in data_sources:
            self.jira_url = data_sources['jira'].config.get('url')
    
    def process_query(self, query: str) -> None:
        """Process a query through Ollama.
        
        Args:
            query: Query string to process
        """
        try:
            # Check if query is a ticket ID
            ticket_match = re.match(r'^([A-Z]+-\d+)$', query.strip())
            if ticket_match:
                self._handle_ticket_query(ticket_match.group(1))
                return
            
            # Build context for Ollama
            context = {
                "last_viewed": self.last_viewed,
                "data_sources": list(self.data_sources.keys())
            }
            
            # Get response from Ollama
            response = self.ollama.query(query, context)
            
            # Try to parse as JSON command
            try:
                command = json.loads(response)
                self._execute_command(command)
            except json.JSONDecodeError:
                # Not a JSON command, just display the response
                console.print(response)
                
        except Exception as e:
            self.logger.exception("Error processing query")
            display_error(str(e))
    
    def _handle_ticket_query(self, ticket_id: str) -> None:
        """Handle a ticket ID query.
        
        Args:
            ticket_id: Ticket ID to fetch and summarize
        """
        if 'jira' not in self.data_sources:
            display_error("JIRA data source not configured")
            return
            
        # Fetch ticket
        command = {
            "type": "jql",
            "query": f"key = {ticket_id}",
            "limit": 1
        }
        
        if self.verbose:
            self.logger.info(f"Generated command: {json.dumps(command)}")
            
        result = self.data_sources['jira'].query(command)
        if not result.success:
            display_error(result.message)
            return
            
        # Update last viewed
        self.last_viewed = ticket_id
        
        # Get ticket data
        if not result.data or not isinstance(result.data, list) or not result.data:
            display_error(f"No ticket found with ID {ticket_id}")
            return
            
        ticket = result.data[0]
        
        # Send ticket data to Ollama for summarization
        context = {
            "last_viewed": ticket_id,
            "ticket_data": json.dumps(ticket, indent=2)
        }
        
        summary = self.ollama.query("Summarize this ticket", context)
        console.print(summary)
    
    def _execute_command(self, command: Dict) -> None:
        """Execute a command from Ollama.
        
        Args:
            command: Command dictionary to execute
        """
        command_type = command.get('type')
        
        if command_type == 'jql':
            if 'jira' not in self.data_sources:
                display_error("JIRA data source not configured")
                return
                
            # Show generated JQL if verbose
            if self.verbose:
                self.logger.info(f"Generated command: {json.dumps(command)}")
                
            result = self.data_sources['jira'].query(command)
            if result.success:
                # Update last viewed if it's a single ticket query
                if command.get('limit', 5) == 1:
                    self.last_viewed = command['query'].split('=')[1].strip()
                display_jira_result(result)
            else:
                display_error(result.message)
            
        elif command_type == 'read_file':
            if 'files' not in self.data_sources:
                display_error("File data source not configured")
                return
                
            # Show generated command if verbose
            if self.verbose:
                self.logger.info(f"Generated command: {json.dumps(command)}")
                
            result = self.data_sources['files'].query(command)
            if result.success:
                display_file_result(result)
            else:
                display_error(result.message)
            
        else:
            display_error(f"Unknown command type: {command_type}")
    
    def handle_open(self) -> None:
        """Handle the open command."""
        if not self.last_viewed:
            display_warning("No item has been viewed yet")
            return
            
        if not self.jira_url:
            display_error("JIRA URL not configured")
            return
            
        # Construct ticket URL
        ticket_url = f"{self.jira_url.rstrip('/')}/browse/{self.last_viewed}"
        
        try:
            # Open URL in default browser
            webbrowser.open(ticket_url)
            console.print(f"Opening {self.last_viewed} in browser...")
        except Exception as e:
            display_error(f"Failed to open browser: {str(e)}")