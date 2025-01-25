import os
import yaml
import logging
import time
import signal
import sys
from dotenv import load_dotenv
from services.core.docker_manager import DockerManager
from services.core.message_processor import MessageProcessor

logger = logging.getLogger('orchai')

class Orchestrator:
    def __init__(self):
        load_dotenv()
        self.rocket_url = os.getenv('ROCKETCHAT_URL')
        if not self.rocket_url:
            raise ValueError("ROCKETCHAT_URL environment variable is required")
            
        self.docker_manager = DockerManager()
        self.message_processor = MessageProcessor()
        self.bots = {}
        self.timestamp = int(time.time())
        self.last_message_ts = None
        
        # Set up signal handlers for immediate cleanup
        signal.signal(signal.SIGINT, self._immediate_shutdown)
        signal.signal(signal.SIGTERM, self._immediate_shutdown)
        
        self.load_bots()

    def load_bots(self):
        """Load bot configurations from team/ directory"""
        team_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'team')
        if not os.path.exists(team_dir):
            os.makedirs(team_dir)
            
        logger.debug("Loading bot configurations")
        
        # First pass: Load all bot configurations
        for config_file in os.listdir(team_dir):
            if config_file.endswith('.yaml'):
                logger.debug(f"Processing config file: {config_file}")
                with open(os.path.join(team_dir, config_file)) as f:
                    config = yaml.safe_load(f)
                    bot_type = config['role']
                    
                    # Create Docker container for the bot
                    self.docker_manager.create_bot_container(bot_type, config, self.timestamp)
                    
                    if bot_type == 'pm':
                        from bots import PMBot
                        logger.debug("Initializing PM bot")
                        self.bots['pm'] = PMBot(config, self.rocket_url, self.docker_manager.docker_client)
                    elif bot_type == 'dev':
                        from bots import DevBot
                        logger.debug("Initializing Dev bot")
                        self.bots['dev'] = DevBot(config, self.rocket_url, self.docker_manager.docker_client)

        # Second pass: Set up bot relationships
        if 'pm' in self.bots and 'dev' in self.bots:
            logger.debug("Setting up bot relationships")
            self.bots['pm'].set_dev_bot(self.bots['dev'])

    def _immediate_shutdown(self, signum, frame):
        """Handle shutdown signals with immediate cleanup"""
        logger.info("Received shutdown signal. Performing immediate cleanup...")
        self._cleanup()
        # Exit immediately without waiting
        os._exit(0)

    def _cleanup(self):
        """Clean up resources immediately"""
        logger.info("Cleaning up resources...")
        try:
            self.docker_manager.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            # Continue with exit even if cleanup fails

    def start(self):
        """Start monitoring #general channel"""
        logger.info("OrchAI is starting up...")
        
        # Get PM bot's channel info
        if 'pm' not in self.bots:
            raise Exception("PM bot is required but not configured")
            
        logger.debug("Getting #general channel info")
        general_channel = self.bots['pm'].channels_info(channel='general').json()
        if not general_channel.get('success'):
            raise Exception("Failed to find #general channel")

        channel_id = general_channel['channel']['_id']
        logger.debug(f"Found #general channel ID: {channel_id}")

        # Have bots say hello
        logger.debug("Sending bot hello messages")
        for bot_type, bot in self.bots.items():
            try:
                message = f"Hello #general! I'm the {bot_type} bot and I'm online and ready to help."
                logger.debug(f"Sending hello message for {bot_type} bot")
                bot.send_message(message)
            except Exception as e:
                logger.error(f"Failed to send hello message for {bot_type} bot: {str(e)}")

        # Subscribe to messages
        logger.debug("Subscribing to channel history")
        history = self.bots['pm'].channels_history(room_id=channel_id).json()
        if history.get('messages'):
            self.last_message_ts = history['messages'][0].get('ts')
        
        logger.info("OrchAI is running. Monitoring #general channel...")
        
        try:
            # In a real implementation, we would use WebSocket for real-time messages
            # For MVP, we'll use polling
            while True:
                messages = self.bots['pm'].channels_history(
                    room_id=channel_id
                ).json()['messages']
                
                # Process only new messages
                for message in messages:
                    if not self.last_message_ts or message.get('ts') > self.last_message_ts:
                        self.message_processor.process_message(message, self.bots)
                        self.last_message_ts = message.get('ts')
                
                time.sleep(1)  # Avoid hammering the API
        except KeyboardInterrupt:
            # Handle Ctrl+C with immediate cleanup
            logger.info("Shutting down OrchAI...")
            self._cleanup()
            os._exit(0)
        except Exception as e:
            # Handle other exceptions with immediate cleanup
            logger.error(f"Error processing messages: {str(e)}")
            self._cleanup()
            os._exit(1)