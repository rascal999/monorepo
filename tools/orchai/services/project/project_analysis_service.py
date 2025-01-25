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
            # Check for direct project creation
            if 'project called' in msg_text.lower():
                return True

            # Use AI for other potential project requests
            system_prompt = """You are a project management bot. Analyze user messages to determine if they're requesting a new project.
            Respond with 'YES' if it's a project request, 'NO' otherwise."""
            
            is_project_request = self.ai_service.get_response(msg_text, system_prompt).strip().upper() == 'YES'
            logger.debug(f"AI analysis result - is project request: {is_project_request}")

            return is_project_request

        except Exception as e:
            logger.error(f"Error analyzing project request: {str(e)}")
            self.message_service("I encountered an error while processing your request. Please try again.")
            return False