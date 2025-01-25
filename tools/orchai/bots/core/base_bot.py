import logging
from ..services.rocket_chat import RocketChatService
from ..services.git_service import GitService
from ..services.ai_service import AIService
from ..services.command_service import CommandService

logger = logging.getLogger('orchai.bot')

class BaseBot:
    def __init__(self, config, rocket_url, docker_client):
        self.config = config
        self.username = config['username']
        
        # Initialize RocketChat service
        self.rocket = RocketChatService(
            rocket_url,
            config['rocketchat']['token'],
            config['rocketchat']['user_id']
        )
        
        # Initialize AI service
        self.ai = AIService(
            model=config['model'],
            docker_client=docker_client
        )
        
        # Initialize Git service
        self.git = GitService(
            user_name=config['git']['user_name'],
            user_email=config['git']['user_email']
        )
        
        # Initialize Command service with permissions
        self.command = CommandService(
            permissions=config.get('permissions', [])
        )
        
        logger.debug(f"Initializing {self.username} bot: {config['name']}")

    def send_message(self, msg):
        """Send a message to #general"""
        try:
            logger.debug(f"{self.username} sending message: {msg}")
            self.rocket.send_message(msg, self.username)
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise

    def channels_info(self, channel):
        """Get channel info"""
        try:
            return self.rocket.channels_info(channel)
        except Exception as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            raise

    def channels_history(self, room_id):
        """Get channel history"""
        try:
            return self.rocket.channels_history(room_id)
        except Exception as e:
            logger.error(f"Failed to get channel history: {str(e)}")
            raise