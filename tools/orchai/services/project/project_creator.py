import logging

logger = logging.getLogger('orchai.bot.pm.creator')

class ProjectCreator:
    def __init__(self, git_service, ai_service, message_service):
        self.git_service = git_service
        self.ai_service = ai_service
        self.message_service = message_service
        self.dev_bot = None

    def set_dev_bot(self, dev_bot):
        """Set reference to dev bot configuration"""
        self.dev_bot = dev_bot

    def create_project(self, project_name, description, username=None):
        """Create project and coordinate with dev bot"""
        try:
            if not self.dev_bot:
                raise Exception("Dev bot configuration not found")

            # Create repository
            repo_name = project_name.lower().replace(' ', '_')
            logger.debug(f"Creating repository: {repo_name}")
            repo = self.git_service.create_repo(repo_name)
            
            # Notify user about repo creation
            self._send_message(f"I've created a repository for your project: {repo_name}", username)
            
            # Generate concise instructions for Dev bot using AI
            logger.debug("Generating instructions for Dev bot")
            system_prompt = """You are a project management bot. Create BRIEF, focused instructions for the development team.
            Keep the response under 500 words. Focus on essential technical tasks and requirements only."""
            
            dev_instructions = self.ai_service.get_response(
                f"Project: {project_name}\nDescription: {description}",
                system_prompt
            )
            
            # Delegate to Dev bot with AI-generated instructions
            logger.debug("Delegating to Dev bot")
            self.message_service(
                f"@{self.dev_bot.username} Please initialize project {repo_name} "
                f"with the following specifications:\n{dev_instructions}"
            )
            
            # Notify user about dev bot delegation
            self._send_message(
                f"I've asked the dev bot to set up your project. "
                f"They'll create the initial project structure based on your requirements.",
                username
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            self._send_message(f"I ran into an issue creating your project: {str(e)}", username)
            return False

    def _send_message(self, msg, username=None):
        """Send a message with proper @username prefix"""
        if username:
            self.message_service(f"@{username} {msg}")
        else:
            self.message_service(msg)