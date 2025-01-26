#!/usr/bin/env python3

import os
import time
import json
import re
import requests
import xml.etree.ElementTree as ET
from rocketchat_API.rocketchat import RocketChat

class XMLCommandProcessor:
    def __init__(self, bot):
        self.bot = bot

    def extract_commands(self, text):
        """Extract XML commands from text."""
        # Find all XML-style commands
        pattern = r'<(\w+)>(.*?)</\1>'
        commands = re.finditer(pattern, text, re.DOTALL)
        return list(commands)

    def execute_command(self, command_name, command_content):
        """Execute a specific XML command."""
        if hasattr(self, f'cmd_{command_name}'):
            try:
                return getattr(self, f'cmd_{command_name}')(command_content)
            except Exception as e:
                return f"Error executing {command_name}: {str(e)}"
        return f"Unknown command: {command_name}"

    def cmd_read_file(self, content):
        """Handle read_file command."""
        try:
            path = re.search(r'<path>(.*?)</path>', content).group(1)
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def cmd_execute_command(self, content):
        """Handle execute_command."""
        try:
            command = re.search(r'<command>(.*?)</command>', content).group(1)
            import subprocess
            # Use zsh -c for command execution
            result = subprocess.run(['zsh', '-c', command], capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def cmd_write_to_file(self, content):
        """Handle write_to_file command."""
        try:
            path = re.search(r'<path>(.*?)</path>', content).group(1)
            file_content = re.search(r'<content>(.*?)</content>', content, re.DOTALL).group(1)
            with open(path, 'w') as f:
                f.write(file_content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def process_commands(self, text):
        """Process all XML commands in text and return results."""
        commands = self.extract_commands(text)
        results = []
        
        for match in commands:
            command_name = match.group(1)
            command_content = match.group(2)
            result = self.execute_command(command_name, command_content)
            results.append(f"Command {command_name} result:\n{result}")
        
        return "\n\n".join(results) if results else None

class Bot:
    def __init__(self):
        # Load environment variables
        self.name = os.environ['BOT_NAME']
        self.username = os.environ['BOT_USERNAME']
        self.role = os.environ['BOT_ROLE']
        self.model = os.environ['BOT_MODEL']
        self.prompt = os.environ['BOT_PROMPT']
        
        # Initialize command processor
        self.command_processor = XMLCommandProcessor(self)
        
        # Initialize Rocket.Chat client
        self.rocket = RocketChat(
            user_id=os.environ['ROCKETCHAT_USER_ID'],
            auth_token=os.environ['ROCKETCHAT_TOKEN'],
            server_url=os.environ.get('ROCKETCHAT_URL', 'http://rocketchat:3000')
        )

        # Send hello message
        self.send_hello()

    def send_hello(self):
        """Send initial hello message to general channel."""
        self.rocket.chat_post_message(
            channel='general',
            text=f"Hello! I'm {self.name}, ready to help with development tasks. Mention me using @{self.username} to get started."
        )

    def handle_message(self, message):
        """Process incoming message and generate response."""
        # Extract message content
        text = message.get('msg', '')
        channel_id = message.get('rid')
        
        # Skip messages not mentioning this specific bot
        mention = f'@{self.username}'
        if mention not in text:
            return

        try:
            # First check for XML commands
            command_results = self.command_processor.process_commands(text)
            if command_results:
                self.rocket.chat_post_message(
                    channel=channel_id,
                    text=command_results
                )
                return

            # If no XML commands, process with AI
            # Remove the @username from the text
            text = text.replace(mention, '').strip()
            
            conversation = [{
                "role": "system",
                "content": self.prompt
            }, {
                "role": "user",
                "content": text
            }]

            # Call AI model through OpenRouter
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": conversation
                }
            )
            
            # Extract and send AI response
            ai_message = response.json()['choices'][0]['message']['content']
            
            # Check if AI response contains XML commands
            command_results = self.command_processor.process_commands(ai_message)
            if command_results:
                self.rocket.chat_post_message(
                    channel=channel_id,
                    text=command_results
                )
            else:
                self.rocket.chat_post_message(
                    channel=channel_id,
                    text=ai_message
                )

        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.rocket.chat_post_message(
                channel=channel_id,
                text=error_msg
            )

    def run(self):
        """Main bot loop."""
        print(f"Bot {self.name} starting up...")
        
        # Subscribe to messages
        last_update = time.time()
        
        while True:
            try:
                # Get new messages
                messages = self.rocket.channels_history(
                    room_id='GENERAL',  # Replace with actual room ID
                    oldest=last_update
                ).json()
                
                # Process each message
                for message in messages.get('messages', []):
                    self.handle_message(message)
                
                # Update timestamp
                last_update = time.time()
                
                # Small delay to prevent excessive API calls
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(5)  # Longer delay on error

if __name__ == "__main__":
    bot = Bot()
    bot.run()