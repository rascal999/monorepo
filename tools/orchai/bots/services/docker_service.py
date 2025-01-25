import os
import logging

logger = logging.getLogger('orchai.bot')

class DockerService:
    def __init__(self, docker_client):
        self.docker_client = docker_client

    def run_command(self, image, command):
        """Run a command in a Docker container"""
        logger.debug(f"Running Docker command: {command} (image: {image})")
        container = self.docker_client.containers.run(
            image,
            command,
            detach=True,
            volumes={
                '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))): {
                    'bind': '/orchai',
                    'mode': 'rw'
                }
            }
        )
        return container