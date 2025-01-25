import logging

logger = logging.getLogger('orchai.bot.pm.analysis')

class ProjectAnalysisService:
    def __init__(self, ai_service, message_service):
        self.ai_service = ai_service
        self.message_service = message_service

    def analyze_project_request(self, msg_text, is_bot_message=False):
        """Analyze if a message is requesting a new project"""
        # Skip bot messages
        if is_bot_message:
            return False

        try:
            system_prompt = """You are a project management bot. Analyze user messages to determine if they're requesting a new project.
            Respond with 'YES' if it's a project request, 'NO' otherwise."""
            
            is_project_request = self.ai_service.get_response(msg_text, system_prompt).strip().upper() == 'YES'
            logger.debug(f"AI analysis result - is project request: {is_project_request}")

            return is_project_request

        except Exception as e:
            logger.error(f"Error analyzing project request: {str(e)}")
            self.message_service("I encountered an error while processing your request. Please try again.")
            return False

    def validate_project_name(self, name):
        """Validate if a project name is appropriate"""
        system_prompt = """You are a project management bot. Validate if the provided project name is appropriate.
        Respond with 'VALID: <name>' if acceptable, or 'INVALID: <reason>' if not."""
        
        validation = self.ai_service.get_response(name, system_prompt)
        logger.debug(f"Name validation result: {validation}")
        
        return validation.startswith('VALID:'), validation.split(':', 1)[1].strip()

    def analyze_requirements(self, description):
        """Analyze project description and extract requirements"""
        system_prompt = """You are a project management bot. Analyze the project description and extract key requirements.
        Format the response as a clear, structured list of requirements."""
        
        analyzed_requirements = self.ai_service.get_response(description, system_prompt)
        logger.debug(f"Requirements analysis result length: {len(analyzed_requirements)}")
        
        return analyzed_requirements

    def generate_dev_instructions(self, project_details):
        """Generate detailed instructions for the development team"""
        system_prompt = """You are a project management bot. Create clear, detailed instructions for the development team
        based on the project requirements. Include specific technical tasks and considerations."""
        
        dev_instructions = self.ai_service.get_response(
            f"Project: {project_details['name']}\n"
            f"Description: {project_details['description']}\n"
            f"Requirements: {project_details['analyzed_requirements']}",
            system_prompt
        )
        
        return dev_instructions