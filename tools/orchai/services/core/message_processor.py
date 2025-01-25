import logging

logger = logging.getLogger('orchai.messages')

class MessageProcessor:
    def __init__(self):
        pass

    def process_message(self, message, bots):
        """Process incoming messages and route to appropriate bots"""
        msg_text = message.get('msg', '').strip()
        username = message.get('u', {}).get('username')
        logger.debug(f"Processing message from {username}: {msg_text}")
        
        # PM bot can respond to any message
        if 'pm' in bots:
            bots['pm'].process_message(message)
        
        # Dev bot only responds to mentions from PM bot
        if 'dev' in bots:
            bots['dev'].process_message(message)