import json
from datetime import datetime
from color_utils import Colors

class BaseCommandHandler:
    def __init__(self, jira_client, history_manager):
        self.jira = jira_client
        self.history = history_manager
        self.last_issue = None

    def format_datetime(self, dt_str, include_time=False):
        """Format datetime string from Jira"""
        if not dt_str:
            return "No date"
        dt = datetime.strptime(dt_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S' if include_time else '%Y-%m-%d')

    def format_ticket_info(self, issue):
        """Format ticket information with timestamps"""
        created = self.format_datetime(issue.fields.created)
        updated = self.format_datetime(issue.fields.updated)
        timestamps = f"Created: {created}, Updated: {updated}"
        return Colors.format_ticket(issue.key, issue.fields.summary, issue.fields.status.name, timestamps)

    def add_to_history(self, command, result, current_ticket=None, ticket_data=None):
        """Add command and result to history"""
        if result:
            self.history.add_entry(command, result, current_ticket, ticket_data)

    def error(self, message):
        """Print error message"""
        error_msg = Colors.colorize(message, Colors.RED)
        print(error_msg)
        return error_msg

    def success(self, message):
        """Print success message"""
        success_msg = Colors.colorize(message, Colors.GREEN)
        print(success_msg)
        return success_msg

    def warning(self, message):
        """Print warning message"""
        warning_msg = Colors.colorize(message, Colors.YELLOW)
        print(warning_msg)
        return warning_msg

    def info(self, message, color=Colors.WHITE):
        """Print info message"""
        info_msg = Colors.colorize(message, color)
        print(info_msg)
        return info_msg

    def execute(self, command, current_ticket=None, ticket_data=None):
        """Base execute method"""
        try:
            cmd = json.loads(command)
            handler_name = f"handle_{cmd['type']}"
            handler = getattr(self, handler_name, None)
            
            if handler:
                return handler(cmd, current_ticket, ticket_data)
            else:
                return self.error(f"Unknown command type: {cmd['type']}")
                
        except json.JSONDecodeError:
            return self.error("Invalid command format")
        except Exception as e:
            return self.error(f"Error executing command: {e}")

    def get_command_context(self, query):
        """Get context for generating commands"""
        raise NotImplementedError("Subclasses must implement get_command_context")