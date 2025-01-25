import os
import logging
import docker

logger = logging.getLogger('orchai.docker')

class DockerManager:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.bot_containers = {}

    def create_bot_container(self, bot_type, config, timestamp):
        """Create a Docker container for a bot"""
        logger.debug(f"Creating container for {bot_type} bot")
        try:
            container_name = f'orchai_{bot_type}_{config["name"]}_{timestamp}'
            container = self.docker_client.containers.run(
                'python:3.12-slim',
                command='tail -f /dev/null',  # Keep container running
                detach=True,
                name=container_name,
                auto_remove=True,  # Automatically remove container when it stops
                volumes={
                    '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                    os.path.abspath(os.path.dirname(os.path.dirname(__file__))): {
                        'bind': '/orchai',
                        'mode': 'rw'
                    }
                },
                environment={
                    'ROCKETCHAT_URL': os.getenv('ROCKETCHAT_URL'),
                    'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
                    'BOT_TYPE': bot_type,
                    'BOT_NAME': config['name']
                }
            )
            logger.debug(f"Container created for {bot_type} bot: {container.id}")
            self.bot_containers[bot_type] = container
            return container
        except Exception as e:
            logger.error(f"Failed to create container for {bot_type} bot: {str(e)}")
            raise

    def cleanup(self):
        """Clean up all containers immediately without waiting"""
        logger.info("Cleaning up Docker containers...")
        for bot_type, container in self.bot_containers.items():
            try:
                logger.debug(f"Killing container for {bot_type} bot: {container.id}")
                container.kill()  # Use kill instead of stop for immediate termination
            except Exception as e:
                logger.error(f"Error killing container {container.id}: {str(e)}")
        self.bot_containers = {}