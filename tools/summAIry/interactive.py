import sys
import re
from jira_client import JiraTicketManager
from ollama_client import OllamaClient
from history_manager import HistoryManager
from command_executor import CommandExecutor

class InteractiveSession:
    def __init__(self, jira_manager, ollama_client):
        self.jira = jira_manager
        self.ollama = ollama_client
        self.last_ticket = None
        self.last_summary = None
        self.chat_history = []
        self.ticket_data = None
        
        # Initialize managers
        self.history = HistoryManager()
        self.executor = CommandExecutor(self.jira.client, self.history)

    def is_ticket_id(self, text):
        """Check if input matches ticket ID pattern"""
        return bool(re.match(r'^[A-Z]+-\d+$', text))

    def process_ticket(self, ticket_id):
        """Process a Jira ticket"""
        issues = self.jira.get_related_tickets(ticket_id)
        if not issues:
            print("No tickets found or accessible", file=sys.stderr)
            return False

        print(f"Found {len(issues)} related tickets", file=sys.stderr)
        print("Formatting ticket data...", file=sys.stderr)
        self.ticket_data = self.jira.format_ticket_data(issues)

        summary = self.ollama.generate_summary(self.ticket_data, detailed=True)
        if summary:
            self.last_ticket = ticket_id
            self.last_summary = summary
            self.chat_history = []  # Reset chat history after new ticket
            print("\n" + summary)
            # Add to command history
            self.history.add_entry(f"Analyze ticket {ticket_id}", summary, ticket_id, self.ticket_data)
            return True
        return False

    def process_query(self, query):
        """Process a free text query"""
        # Generate appropriate command based on context
        context = self.executor.get_command_context(
            query,
            self.last_ticket,
            self.last_summary,
            self.ticket_data,
            self._format_chat_history()
        )
        
        response = self.ollama.generate_response(context, query)
        if not response:
            return False

        # Check if response is a command (JSON format)
        try:
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return self.executor.execute(response, self.last_ticket, self.ticket_data)
        except:
            pass

        # If not a command and we have ticket context, treat as normal response
        if self.last_ticket and self.ticket_data:
            self.chat_history.append(("user", query))
            self.chat_history.append(("assistant", response))
            # Add to command history
            self.history.add_entry(query, response, self.last_ticket, self.ticket_data)
            print("\n" + response)
            return True
        else:
            print("No ticket context available. Please analyze a ticket first.")
            return False

    def _format_chat_history(self):
        """Format chat history for context"""
        if not self.chat_history:
            return "No previous chat messages"
        
        formatted = []
        for role, message in self.chat_history:
            formatted.append(f"{role}: {message}")
        return "\n".join(formatted)

    def run(self):
        """Run interactive session"""
        print("Enter a ticket ID (e.g., PROJ-123) to analyze it")
        print("Or enter any question about tickets")
        print("Type 'exit' to quit")
        print("Use up/down arrows for command history\n")

        while True:
            try:
                user_input = input("> ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    break

                if self.is_ticket_id(user_input):
                    self.process_ticket(user_input)
                else:
                    self.process_query(user_input)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)