#!/usr/bin/env python3

import os
import yaml
import docker
import signal
import sys
from pathlib import Path
from dotenv import load_dotenv

class OrchAI:
    def __init__(self):
        load_dotenv()
        self.docker_client = docker.from_env()
        self.team_dir = Path(__file__).parent / 'team'
        self.bots = {}
        self.containers = []
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

    def cleanup(self, signum, frame):
        """Clean up containers on shutdown."""
        print("\nShutting down bots...")
        for container in self.containers:
            try:
                container.stop()
                container.remove()
                print(f"Stopped and removed container {container.id}")
            except Exception as e:
                print(f"Error cleaning up container {container.id}: {str(e)}")
        sys.exit(0)

    def build_bot_image(self):
        """Build the bot Docker image."""
        try:
            print("Building bot Docker image...")
            build_path = Path(__file__).parent
            
            image, logs = self.docker_client.images.build(
                path=str(build_path),
                tag='orchai2-bot'
            )
            print("Successfully built bot image")
            return True
        except Exception as e:
            print(f"Failed to build bot image: {str(e)}")
            return False

    def load_bot_configs(self):
        """Load bot configurations from YAML files in team directory."""
        for yaml_file in self.team_dir.glob('*.yaml'):
            if yaml_file.name == 'example.yaml':
                continue
            
            with open(yaml_file) as f:
                config = yaml.safe_load(f)
                self.bots[config['name']] = config

    def launch_bot(self, name, config):
        """Launch a Docker container for a bot."""
        # Load base prompt
        with open(self.team_dir / 'prompt.txt') as f:
            base_prompt = f.read()

        # Combine base prompt with bot's custom prompt
        full_prompt = base_prompt + "\n\n" + config.get('prompt', '')

        # Prepare environment variables from config
        environment = {
            'BOT_NAME': name,
            'BOT_USERNAME': config['username'],
            'BOT_ROLE': config['role'],
            'BOT_MODEL': config['model'],
            'ROCKETCHAT_USER_ID': config['rocketchat']['user_id'],
            'ROCKETCHAT_TOKEN': config['rocketchat']['token'],
            'GIT_USER_NAME': config['git']['user_name'],
            'GIT_USER_EMAIL': config['git']['user_email'],
            'BOT_PROMPT': full_prompt,
            'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY', ''),
            'ROCKETCHAT_URL': os.getenv('ROCKETCHAT_URL', 'http://rocketchat:3000')
        }

        # Prepare container configuration
        container_config = {
            'image': 'orchai2-bot',
            'environment': environment,
            'volumes': {
                config['volume'].split(':')[0]: {
                    'bind': config['volume'].split(':')[1],
                    'mode': 'rw'
                }
            },
            'detach': True,
            'remove': True,  # Auto-remove container when stopped
            'network_mode': 'host'  # Use host networking to access Docker and Rocket.Chat
        }

        # Launch container
        container = self.docker_client.containers.run(**container_config)
        print(f"Launched bot {name} in container {container.id}")
        self.containers.append(container)
        return container

    def run(self):
        """Main execution flow."""
        print("Starting OrchAI system...")
        print("Press Ctrl+C to stop all bots and exit")
        
        # Build bot image first
        if not self.build_bot_image():
            print("Failed to build bot image, exiting...")
            return

        # Load bot configurations
        self.load_bot_configs()
        print(f"Loaded {len(self.bots)} bot configurations")

        # Launch bot containers
        for name, config in self.bots.items():
            try:
                container = self.launch_bot(name, config)
                print(f"Successfully launched bot: {name}")
            except Exception as e:
                print(f"Failed to launch bot {name}: {str(e)}")

        # Keep the script running to maintain containers
        try:
            signal.pause()
        except KeyboardInterrupt:
            self.cleanup(None, None)

if __name__ == "__main__":
    orchai = OrchAI()
    orchai.run()