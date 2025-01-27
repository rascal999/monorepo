"""JIRA command handling functionality."""
import json
import logging
from typing import Dict, Optional

from ..display import display_error, display_jira_result, console


class JIRAMixin:
    """Mixin for JIRA command operations."""

    def _handle_ticket_query(self, ticket_id: str) -> None:
        """Handle a JIRA ticket query.
        
        Args:
            ticket_id: JIRA ticket ID to fetch
        """
        if 'jira' not in self.data_sources:
            display_error("JIRA data source not configured")
            return
            
        # Build query context
        context = {
            "scope": "ticket",
            "limit": 1
        }
        
        # Fetch ticket
        command = {
            "type": "jql",
            "query": f"key = {ticket_id}",
            "context": context
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
            "last_viewed": self.last_viewed,
            "ticket_data": json.dumps(ticket, indent=2)
        }
        
        summary = self.ollama.query(f"Summarize this ticket", context)
        console.print(summary)
        
        # Cache summary
        self.ticket_summaries[ticket_id] = summary

    def _execute_jira_command(self, command: Dict) -> Optional[None]:
        """Execute a JIRA command.
        
        Args:
            command: Command dictionary to execute
        """
        if 'jira' not in self.data_sources:
            display_error("JIRA data source not configured")
            return
            
        cmd = command.get('command')
        params = command.get('params', {})
        
        logging.debug(f"Executing JIRA command: cmd={cmd}, params={json.dumps(params)}")
        
        if cmd == 'add_comment':
            message = params.get('message')
            if not message:
                display_error("Missing comment message")
                return
                
            # Get ticket ID and message from params
            ticket_id = params.get('ticket')
            if not ticket_id:
                display_error("Missing ticket ID")
                return
                
            # Show comment preview and get confirmation
            console.print(f"\nTicket: {ticket_id}")
            console.print("Comment to be added:")
            console.print(message)
            # Get user confirmation
            confirmation = input("\nAre you sure you want to add this comment? [y/N] ").lower()
            if confirmation != 'y':
                console.print("Comment cancelled")
                return
                
            result = self.data_sources['jira'].add_comment(ticket_id, message)
            if result.success:
                console.print(result.message)
            else:
                display_error(result.message)
                
        elif cmd == 'delete_ticket':
            tickets = params.get('tickets', [])
            if not tickets:
                display_error("No tickets specified")
                return
                
            # Show confirmation prompt
            console.print("\nTickets to delete:")
            for ticket in tickets:
                console.print(f"- {ticket}")
            console.print("\nAre you sure you want to delete these tickets? [y/N] ", end="", markup=False)
            
            # Get user confirmation
            confirmation = input().lower()
            if confirmation != 'y':
                console.print("Delete cancelled")
                return
                
            result = self.data_sources['jira'].delete_ticket(tickets)
            if result.success:
                console.print(result.message)
                return None  # Command fully handled
            else:
                display_error(result.message)
                return None  # Error already displayed
                
        elif cmd == 'fetch_ticket':
            ticket = params.get('ticket')
            limit = params.get('limit', 1)
            if not ticket:
                display_error("Missing ticket ID")
                return
                
            command = {
                "type": "jql",
                "query": f"key = {ticket}",
                "limit": limit
            }
            self._execute_jql_command(command)
            
        else:
            display_error(f"Unknown JIRA command: {cmd}")
            
    def _execute_jql_command(self, command: Dict) -> None:
        """Execute a JQL query command.
        
        Args:
            command: Command dictionary to execute
        """
        if self.verbose:
            self.logger.info(f"Generated command: {json.dumps(command)}")
            
        result = self.data_sources['jira'].query(command)
        if result.success:
            display_jira_result(result)
        else:
            display_error(result.message)