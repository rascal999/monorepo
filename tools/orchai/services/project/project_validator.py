import logging

logger = logging.getLogger('orchai.bot.pm.validator')

class ProjectValidator:
    def __init__(self, ai_service, message_service):
        self.ai_service = ai_service
        self.message_service = message_service

    def validate_name(self, name):
        """Validate project name"""
        if not name or name.isspace():
            return False, None

        # Clean up name
        name = name.strip().lower()
        
        # Basic validation
        if not all(c.isalnum() or c in '-_' for c in name):
            return False, None

        # Common project names are always valid
        if name in ['hello-world', 'hello_world', 'helloworld']:
            return True, name

        # Use AI for more complex validation
        system_prompt = """You are a project management bot. Validate if the provided project name is appropriate.
        A name is valid if it:
        1. Is not empty
        2. Contains only letters, numbers, hyphens, or underscores
        3. Is reasonably descriptive
        Respond with 'VALID: <name>' if acceptable, or 'INVALID: <reason>' if not."""
        
        validation = self.ai_service.get_response(name, system_prompt)
        logger.debug(f"Name validation result: {validation}")
        
        if validation.startswith('VALID:'):
            return True, name
        else:
            return False, None