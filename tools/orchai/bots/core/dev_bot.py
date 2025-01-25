import os
import logging
from .base_bot import BaseBot
from services.dev.dev_flow_service import DevFlowService

logger = logging.getLogger('orchai.bot.dev')

class DevBot(BaseBot):
    def __init__(self, config, rocket_url, docker_client):
        super().__init__(config, rocket_url, docker_client)
        
        # Initialize services with wrapper for send_message
        message_service = lambda msg: self.send_message(msg)
        
        self.dev_flow = DevFlowService(
            self.ai,
            self.git,
            message_service
        )

    def process_message(self, message):
        """Process messages from #general"""
        username = message.get('u', {}).get('username')
        msg_text = message.get('msg', '').strip()
        logger.debug(f"Processing message from {username}: {msg_text}")

        # Skip own messages
        if username == self.username:
            logger.debug("Skipping own message")
            return

        try:
            # Check if message is meant for this bot
            mention = f'@{self.username}'
            logger.debug(f"Looking for mention: {mention}")
            if mention in msg_text:
                # Split message into lines and find the line with the mention
                lines = msg_text.split('\n')
                for i, line in enumerate(lines):
                    if mention in line:
                        # Extract actual message content starting from the mention line
                        msg_text = '\n'.join([line[line.index(mention) + len(mention):].strip()] + lines[i+1:])
                        break

                logger.debug(f"Processing mention: {msg_text}")
                
                # Check if it's a project handoff
                if "Please initialize project" in msg_text:
                    logger.debug("Handling project handoff")
                    self._handle_project_handoff(msg_text, username)
                else:
                    # Handle other messages through dev flow
                    logger.debug("Handling message through dev flow")
                    self.dev_flow.handle_message(msg_text, username)
            else:
                logger.debug(f"Ignoring message without mention {mention}")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.send_message(f"@{username} I encountered an error. Please try again.")

    def _handle_project_handoff(self, msg_text, username):
        """Handle project handoff from PM bot"""
        try:
            # Extract project name and specifications
            lines = msg_text.split('\n')
            project_name = None
            specifications = []
            
            for line in lines:
                if "Please initialize project" in line:
                    # Extract project name
                    project_name = line.split("project")[1].split("with")[0].strip()
                elif line.strip():
                    # Collect non-empty lines as specifications
                    specifications.append(line.strip())
            
            if project_name and specifications:
                logger.debug(f"Handling project handoff for: {project_name}")
                self.dev_flow.handle_project_handoff(
                    project_name,
                    '\n'.join(specifications),
                    username
                )
                self.send_message(f"@{username} I'll start working on project {project_name}")
            else:
                self.send_message(f"@{username} I couldn't understand the project details. Please try again.")

        except Exception as e:
            logger.error(f"Error handling project handoff: {str(e)}")
            self.send_message(f"@{username} I encountered an error handling the project handoff. Please try again.")