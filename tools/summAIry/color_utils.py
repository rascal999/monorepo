class Colors:
    # ANSI escape codes for colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    @staticmethod
    def status_color(status):
        """Get color for Jira status"""
        status = status.upper()
        if status in ['DONE', 'RESOLVED', 'CLOSED']:
            return Colors.GREEN
        elif status in ['IN PROGRESS', 'REVIEW']:
            return Colors.YELLOW
        elif status in ['BLOCKED', 'ON HOLD']:
            return Colors.RED
        elif status == 'BACKLOG':
            return Colors.BLUE
        else:
            return Colors.WHITE

    @staticmethod
    def colorize(text, color):
        """Wrap text in color and reset"""
        return f"{color}{text}{Colors.RESET}"

    @staticmethod
    def format_ticket(key, summary, status, timestamps):
        """Format ticket with colors"""
        colored_key = Colors.colorize(key, Colors.CYAN + Colors.BOLD)
        colored_status = Colors.colorize(status, Colors.status_color(status))
        colored_timestamps = Colors.colorize(timestamps, Colors.MAGENTA)
        
        return f"• {colored_key}: {summary} ({colored_status}) [{colored_timestamps}]"