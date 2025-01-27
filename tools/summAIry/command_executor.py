from commands.base import BaseCommandHandler
from commands.jql import JQLCommandHandler
from commands.ticket import TicketCommandHandler

class CommandExecutor(BaseCommandHandler):
    def __init__(self, jira_client, history_manager):
        super().__init__(jira_client, history_manager)
        self.handlers = {
            'jql': JQLCommandHandler(jira_client, history_manager),
            'ticket': TicketCommandHandler(jira_client, history_manager)
        }

    def execute(self, command, current_ticket=None, ticket_data=None):
        """Execute a command using appropriate handler"""
        try:
            # First try specific handlers
            if command.startswith('{"type": "jql"') or '"type":"jql"' in command:
                return self.handlers['jql'].execute(command, current_ticket, ticket_data)
            elif any(t in command for t in ['"fetch_ticket"', '"add_comment"', '"comments"']):
                return self.handlers['ticket'].execute(command, current_ticket, ticket_data)
            
            # Fall back to base handler if no specific handler matches
            return super().execute(command, current_ticket, ticket_data)
            
        except Exception as e:
            return self.error(f"Error executing command: {e}")

    def get_command_context(self, query, current_ticket=None, ticket_summary=None, ticket_data=None, chat_history=None):
        """Get combined command context from all handlers"""
        # Get history context
        history_context = self.history.get_context()

        # Get context from JQL handler
        jql_context = self.handlers['jql'].get_command_context(query, history_context)

        # Get context from ticket handler if we have a current ticket
        ticket_context = None
        if current_ticket and ticket_data:
            ticket_context = self.handlers['ticket'].get_command_context(
                query,
                current_ticket,
                ticket_summary,
                ticket_data,
                chat_history,
                history_context
            )

        # Return ticket context if available, otherwise JQL context
        return ticket_context if ticket_context else jql_context