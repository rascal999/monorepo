import logging

logger = logging.getLogger('orchai.bot.dev.task')

class TaskService:
    def __init__(self, command_service, message_service):
        self.command_service = command_service
        self.message_service = message_service
        self.current_task = None
        self.state = {}
        self.current_user = None

    def handle_task(self, msg_text, username=None):
        """Handle ongoing development tasks"""
        if username:
            self.current_user = username

        logger.debug(f"Handling task: {msg_text}")
        try:
            # Execute necessary commands
            if self.command_service.has_permission('command_execution'):
                result = self.command_service.execute(msg_text)
                self._send_message(f"Task execution result:\n{result}")
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            self._send_message(f"Error executing task: {str(e)}")

    def _send_message(self, msg):
        """Send a message with proper @username prefix"""
        if self.current_user:
            self.message_service(f"@{self.current_user} {msg}")
        else:
            self.message_service(msg)

    def set_current_task(self, task):
        """Set the current task being worked on"""
        self.current_task = task

    def get_current_task(self):
        """Get the current task"""
        return self.current_task

    def update_state(self, key, value):
        """Update task state"""
        self.state[key] = value

    def get_state(self, key):
        """Get task state value"""
        return self.state.get(key)

    def reset_state(self):
        """Reset the service's state"""
        self.current_task = None
        self.state = {}
        self.current_user = None