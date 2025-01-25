import os
import logging
import subprocess

logger = logging.getLogger('orchai.bot.command')

class CommandService:
    def __init__(self, permissions=None):
        self.permissions = permissions or []

    def execute(self, command):
        """Execute a command if permitted"""
        try:
            if 'command_execution' not in self.permissions:
                raise Exception("Command execution not permitted")

            logger.debug(f"Executing command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Command failed: {result.stderr}")
                
            return result.stdout
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise

    def check_permission(self, permission):
        """Check if a specific permission is granted"""
        return permission in self.permissions