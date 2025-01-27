import webbrowser
from .base import BaseCommandHandler
from color_utils import Colors

class OpenCommandHandler(BaseCommandHandler):
    def handle_open_last(self, cmd, current_ticket=None, ticket_data=None):
        """Handle opening last ticket in browser"""
        url = self.history.get_last_ticket_url()
        if not url:
            return self.error("No recent ticket found to open")
            
        try:
            webbrowser.open(url)
            result = self.success(f"Opened {url} in default browser")
            self.add_to_history(cmd, result, current_ticket, ticket_data)
            return True
        except Exception as e:
            return self.error(f"Failed to open browser: {e}")

    def get_command_context(self, query, current_ticket=None, ticket_summary=None, ticket_data=None, chat_history=None, history_context=""):
        """Get context for open commands"""
        return f"""Previous ticket summary ({current_ticket or 'None'}):
{ticket_summary or 'No summary'}

Chat history:
{chat_history or 'No previous chat messages'}

{history_context}

Available commands:
1. open_last - Open the last summarized ticket in default browser
   Format: {{"type": "open_last"}}

User query: {query}

If the user's query can be answered using this command, respond with the appropriate command in JSON format.
Otherwise, provide a normal response based on the available context.
"""