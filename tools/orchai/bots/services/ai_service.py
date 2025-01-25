import logging

logger = logging.getLogger('orchai.bot.ai')

class AIService:
    def __init__(self, model, docker_client=None):
        self.model = model
        self.docker_client = docker_client

    def get_response(self, prompt, system_prompt=None):
        """Get AI response for prompt"""
        try:
            # For MVP, return a simple response
            if "analyze" in prompt.lower():
                return [
                    {
                        'description': 'Frontend Development (HTML CSS)',
                        'details': [
                            'Create an HTML file (index.html) containing a single <h1> element with the text "Hello World!"',
                            'Style the <h1> element using CSS for basic presentation'
                        ]
                    }
                ]
            elif "website" in prompt.lower():
                return "website"
            elif "hello-world" in prompt.lower():
                return "hello-world"
            elif "output hello world" in prompt.lower():
                return "VALID"
            elif "yes" in prompt.lower():
                return "CONFIRM"
            else:
                return "UNKNOWN"
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            raise