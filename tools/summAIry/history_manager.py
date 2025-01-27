import readline
import atexit
from pathlib import Path
from collections import deque

class HistoryManager:
    def __init__(self):
        self.command_history = deque(maxlen=10)  # Keep last 10 commands and their results
        self.setup_history()

    def setup_history(self):
        """Setup command history with persistent storage"""
        # Create history file in user's home directory
        history_dir = Path.home() / '.config' / 'summAIry'
        history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = history_dir / 'history'
        
        # Create history file if it doesn't exist
        if not self.history_file.exists():
            self.history_file.touch()

        # Read history file
        readline.read_history_file(str(self.history_file))

        # Set history length
        readline.set_history_length(1000)

        # Save history on exit
        atexit.register(readline.write_history_file, str(self.history_file))

        # Enable tab completion
        readline.parse_and_bind('tab: complete')

    def add_entry(self, command, result, ticket_id=None, ticket_data=None):
        """Add command and result to history"""
        self.command_history.append({
            'command': command,
            'result': result,
            'ticket_id': ticket_id,
            'ticket_data': ticket_data
        })

    def get_context(self):
        """Get formatted history context"""
        if not self.command_history:
            return ""
            
        context = "\nPrevious commands and results:\n"
        for entry in self.command_history:
            context += f"\nCommand: {entry['command']}\n"
            context += f"Result: {entry['result']}\n"
            if entry.get('ticket_id'):
                context += f"Ticket: {entry['ticket_id']}\n"
        return context