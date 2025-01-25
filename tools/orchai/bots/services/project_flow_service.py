import logging

logger = logging.getLogger('orchai.bot.pm.flow')

class ProjectFlowService:
    def __init__(self, ai_service, git_service, message_service):
        self.ai_service = ai_service
        self.git_service = git_service
        self.message_service = message_service
        self.current_project = None
        self.project_requirements = {}
        self.dev_bot = None
        self.current_user = None

    def set_dev_bot(self, dev_bot):
        """Set reference to dev bot configuration"""
        logger.debug("Setting Dev bot reference")
        self.dev_bot = dev_bot

    def handle_project_flow(self, msg_text, username=None):
        """Handle the project creation flow"""
        if username:
            self.current_user = username

        try:
            if not msg_text or msg_text.isspace():
                self._send_message("Please provide a project name.")
                return

            if self.current_project == 'pending_name':
                # Basic validation without AI for common project names
                name = msg_text.strip().lower()
                if name in ['hello-world', 'hello_world', 'helloworld']:
                    self.project_requirements['name'] = name
                    self.current_project = 'pending_description'
                    self._send_message("Great! Now, please provide a brief description of the project.")
                    return

                # Use AI for more complex name validation
                system_prompt = """You are a project management bot. Validate if the provided project name is appropriate.
                A name is valid if it:
                1. Is not empty
                2. Contains only letters, numbers, hyphens, or underscores
                3. Is reasonably descriptive
                Respond with 'VALID: <name>' if acceptable, or 'INVALID: <reason>' if not."""
                
                validation = self.ai_service.get_response(msg_text, system_prompt)
                logger.debug(f"Name validation result: {validation}")
                
                if validation.startswith('VALID:'):
                    self.project_requirements['name'] = msg_text
                    self.current_project = 'pending_description'
                    self._send_message("Great! Now, please provide a brief description of the project.")
                else:
                    self._send_message(f"That name might not work: {validation.split(':', 1)[1].strip()}")

            elif self.current_project == 'pending_description':
                system_prompt = """You are a project management bot. Analyze the project description and extract key requirements.
                Format the response as a clear, structured list of requirements."""
                
                analyzed_requirements = self.ai_service.get_response(msg_text, system_prompt)
                self.project_requirements['description'] = msg_text
                self.project_requirements['analyzed_requirements'] = analyzed_requirements
                self.current_project = 'pending_confirmation'
                self._show_confirmation()

            elif self.current_project == 'pending_confirmation':
                if msg_text.lower() in ['y', 'yes', 'confirm']:
                    self._create_project()
                else:
                    self._send_message("Project creation cancelled.")
                    self.reset_state()

        except Exception as e:
            logger.error(f"Error in project flow: {str(e)}")
            self._send_message("I encountered an error. Project creation cancelled.")
            self.reset_state()

    def _send_message(self, msg):
        """Send a message with proper @username prefix"""
        if self.current_user:
            self.message_service(f"@{self.current_user} {msg}")
        else:
            self.message_service(msg)

    def _show_confirmation(self):
        """Show project details for confirmation"""
        logger.debug("Showing project confirmation")
        confirmation_msg = (
            f"Please confirm the project details:\n"
            f"Name: {self.project_requirements['name']}\n"
            f"Description: {self.project_requirements['description']}\n\n"
            f"Analyzed Requirements:\n{self.project_requirements['analyzed_requirements']}\n\n"
            f"Type 'yes' to confirm or 'no' to cancel."
        )
        self._send_message(confirmation_msg)

    def _create_project(self):
        """Create the project and delegate to Dev bot"""
        try:
            if not self.dev_bot:
                raise Exception("Dev bot configuration not found")

            # Create repository
            repo_name = self.project_requirements['name'].lower().replace(' ', '_')
            logger.debug(f"Creating repository: {repo_name}")
            repo = self.git_service.create_repo(repo_name)
            
            # Notify about repo creation
            self._send_message(f"Created repository: {repo_name}")
            
            # Generate detailed instructions for Dev bot using AI
            logger.debug("Generating instructions for Dev bot")
            system_prompt = """You are a project management bot. Create clear, detailed instructions for the development team
            based on the project requirements. Include specific technical tasks and considerations."""
            
            dev_instructions = self.ai_service.get_response(
                f"Project: {self.project_requirements['name']}\n"
                f"Description: {self.project_requirements['description']}\n"
                f"Requirements: {self.project_requirements['analyzed_requirements']}",
                system_prompt
            )
            
            # Delegate to Dev bot with AI-generated instructions
            logger.debug("Delegating to Dev bot")
            self.message_service(
                f"@{self.dev_bot.username} Please initialize project {repo_name} "
                f"with the following specifications:\n{dev_instructions}"
            )
            
            self.reset_state()
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            self._send_message(f"Error creating project: {str(e)}")
            self.reset_state()

    def reset_state(self):
        """Reset the service's state"""
        logger.debug("Resetting service state")
        self.current_project = None
        self.project_requirements = {}
        self.current_user = None