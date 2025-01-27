from commands.base import BaseCommandHandler
from commands.jql import JQLCommandHandler
from commands.ticket import TicketCommandHandler
from commands.open import OpenCommandHandler

class CommandExecutor(BaseCommandHandler):
    def __init__(self, jira_client, history_manager, debug=False):
        super().__init__(jira_client, history_manager, debug)
        self.handlers = {
            'jql': JQLCommandHandler(jira_client, history_manager, debug),
            'ticket': TicketCommandHandler(jira_client, history_manager, debug),
            'open': OpenCommandHandler(jira_client, history_manager, debug)
        }

    def execute(self, command, current_ticket=None, ticket_data=None):
        """Execute a command using appropriate handler"""
        try:
            self.debug_log(f"Executing command/response: {command}")
            
            # Check if response looks like a command
            if command.strip().startswith('{') and '"type"' in command:
                self.debug_log("Detected command format")
                
                # Handle model commands
                if '"type": "jql"' in command or '"type":"jql"' in command:
                    self.debug_log("Routing to JQL handler")
                    return self.handlers['jql'].execute(command, current_ticket, ticket_data)
                elif any(t in command for t in ['"fetch_ticket"', '"add_comment"']):
                    self.debug_log("Routing to ticket handler")
                    return self.handlers['ticket'].execute(command, current_ticket, ticket_data)
                
                # Fall back to base handler if no specific handler matches
                self.debug_log("No specific handler found, falling back to base handler")
                return super().execute(command, current_ticket, ticket_data)
            else:
                # For non-command responses, just display the text
                self.debug_log("Non-command response, displaying as text")
                print(command)
                return True
            
        except Exception as e:
            self.debug_log(f"Error executing command: {str(e)}")
            self.debug_log(f"Command was: {command}")
            return self.error(f"Error executing command: {e}")

    def get_command_context(self, query, current_ticket=None, ticket_summary=None, ticket_data=None, chat_history=None):
        """Get combined command context from all handlers"""
        self.debug_log(f"Getting command context for query: {query}")
        self.debug_log(f"Current ticket: {current_ticket}")
        
        # Get history context
        history_context = self.history.get_context()
        self.debug_log(f"History context length: {len(history_context) if history_context else 0}")

        # Get context from JQL handler
        jql_context = self.handlers['jql'].get_command_context(query, history_context)
        self.debug_log("Got JQL context")

        # Get context from ticket handler if we have a current ticket
        ticket_context = None
        if current_ticket and ticket_data:
            self.debug_log("Getting ticket context")
            ticket_context = self.handlers['ticket'].get_command_context(
                query,
                current_ticket,
                ticket_summary,
                ticket_data,
                chat_history,
                history_context
            )
            self.debug_log("Got ticket context")

        # Get context from open handler
        self.debug_log("Getting open handler context")
        open_context = self.handlers['open'].get_command_context(
            query,
            current_ticket,
            ticket_summary,
            ticket_data,
            chat_history,
            history_context
        )
        self.debug_log("Got open context")

        # Return ticket context if available, otherwise use JQL context
        # Note: open_last is a user command, not a model command
        if ticket_context:
            self.debug_log("Using ticket context")
            return ticket_context
        else:
            self.debug_log("Using JQL context for general query")
            return jql_context