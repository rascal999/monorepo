import os
import logging
from .base_bot import BaseBot
from services.pm.project_flow_service import ProjectFlowService

logger = logging.getLogger('orchai.bot.pm')

class PMBot(BaseBot):
    def __init__(self, config, rocket_url, docker_client):
        super().__init__(config, rocket_url, docker_client)
        
        # Initialize services with wrapper for send_message
        message_service = lambda msg: self.send_message(msg)
        
        self.project_flow = ProjectFlowService(
            self.ai,
            self.git,
            message_service
        )

    def set_dev_bot(self, dev_bot):
        """Set reference to dev bot configuration"""
        logger.debug("Setting Dev bot reference")
        self.project_flow.set_dev_bot(dev_bot)

    def process_message(self, message):
        """Process messages from #general"""
        username = message.get('u', {}).get('username')
        msg_text = message.get('msg', '').strip()
        logger.debug(f"Processing message from {username}: {msg_text}")

        # Skip own messages
        if username == self.username:
            logger.debug("Skipping own message")
            return

        # Skip messages that start with @ mentions
        if msg_text.startswith('@'):
            logger.debug("Skipping message that starts with @mention")
            return

        # If message contains @dev_bot mention, skip it
        if self.project_flow.dev_bot and f"@{self.project_flow.dev_bot.username}" in msg_text:
            logger.debug("Skipping message meant for dev bot")
            return

        try:
            # Handle message through project flow service
            self.project_flow.handle_project_flow(msg_text, username)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.send_message(f"@{username} I encountered an error. Please try again.")
