import logging
from services.core.state_machine import State

logger = logging.getLogger('orchai.bot.pm.messages')

class ProjectFlowMessages:
    STATE_MESSAGES = {
        State.IDLE: "I'm here to help create new projects! Let me know what you'd like to build.",
        State.COLLECTING_TYPE: "What kind of project would you like to create? For example: a website, an API, a command-line tool, etc.",
        State.COLLECTING_NAME: "Great! What should we call this project?",
        State.COLLECTING_FEATURES: "Perfect! Now, what features should this project have? Please describe what you'd like it to do.",
        State.ANALYZING_REQUIREMENTS: "Analyzing your requirements...",
        State.CONFIRMING: None,  # Uses show_confirmation
        State.CREATING_PROJECT: "Creating your project...",
        State.ERROR_HANDLING: "I encountered an issue. Would you like to try again?",
        State.HANDOFF_TO_DEV: "Handing off to the development team..."
    }

    ERROR_MESSAGES = {
        'unclear_type': "I'm not sure I understand that project type. Could you please clarify?",
        'invalid_name': "That name might not work. Please try a different name using only letters, numbers, hyphens, or underscores.",
        'unclear_requirements': "Could you provide more specific details about the features? This will help ensure I create exactly what you need.",
        'invalid_requirements': "I noticed some potential issues with the requirements. Could you please revise them to be more specific and achievable?",
        'creation_failed': "I had trouble creating the project. Let's try again.",
        'max_errors': "I'm having trouble understanding. Let's start fresh when you're ready.",
        'general_error': "I encountered an error. Please try again."
    }

    def __init__(self, message_service):
        self.message_service = message_service
        self.current_user = None

    def set_user(self, username):
        """Set current user for message context"""
        self.current_user = username

    def send_state_message(self, state):
        """Send message for current state"""
        if message := self.STATE_MESSAGES.get(state):
            self.send_message(message)

    def send_help_message(self, state):
        """Send help message based on current state"""
        help_messages = {
            State.IDLE: "Just tell me what kind of project you'd like to create!",
            State.COLLECTING_TYPE: "Tell me what type of project you want (website, API, CLI tool, etc.)",
            State.COLLECTING_NAME: "Provide a name for your project using letters, numbers, hyphens, or underscores",
            State.COLLECTING_FEATURES: "Describe the features and requirements for your project",
            State.CONFIRMING: "Review the details and confirm if you want to proceed with creation"
        }
        
        help_msg = help_messages.get(state, "How can I help you with your project?")
        self.send_message(help_msg)

    def send_error_message(self, error_type):
        """Send error message by type"""
        if message := self.ERROR_MESSAGES.get(error_type):
            self.send_message(message)

    def show_confirmation(self, requirements):
        """Show project details for confirmation"""
        confirmation_msg = (
            f"Here's what I understand about your project:\n\n"
            f"Type: {requirements.get('type', 'Not specified')}\n"
            f"Name: {requirements.get('name', 'Not specified')}\n"
            f"Features: {requirements.get('features', 'Not specified')}\n\n"
            f"Would you like me to create this project? (You can also edit the type, name, or features)"
        )
        self.send_message(confirmation_msg)

    def send_message(self, msg):
        """Send a message with proper @username prefix"""
        if self.current_user:
            self.message_service(f"@{self.current_user} {msg}")
        else:
            self.message_service(msg)