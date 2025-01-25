import logging
from enum import Enum, auto

logger = logging.getLogger('orchai.bot.pm.intent')

class Intent(Enum):
    CREATE_PROJECT = auto()
    PROVIDE_TYPE = auto()
    PROVIDE_NAME = auto()
    PROVIDE_FEATURES = auto()
    CONFIRM = auto()
    DENY = auto()
    BACK = auto()
    HELP = auto()
    CANCEL = auto()
    EDIT_TYPE = auto()
    EDIT_NAME = auto()
    EDIT_FEATURES = auto()
    UNKNOWN = auto()

class IntentService:
    def __init__(self, ai_service):
        self.ai = ai_service

    def detect_intent(self, message, current_state=None):
        """
        Use AI to detect the intent of a message within the context of the current state
        """
        system_prompt = f"""You are an intent classifier for a project management bot. 
        Current state: {current_state}
        
        Analyze the user's message and classify it into one of these intents:
        - CREATE_PROJECT: User wants to create a new project
        - PROVIDE_TYPE: User is providing project type information
        - PROVIDE_NAME: User is providing a project name
        - PROVIDE_FEATURES: User is describing project features/requirements
        - CONFIRM: User is confirming/agreeing
        - DENY: User is denying/disagreeing
        - BACK: User wants to go back to previous step
        - HELP: User needs help/guidance
        - CANCEL: User wants to cancel/stop
        - EDIT_TYPE: User wants to change project type
        - EDIT_NAME: User wants to change project name
        - EDIT_FEATURES: User wants to change project features
        - UNKNOWN: Message intent cannot be determined

        For example:
        - If in COLLECTING_NAME state and user provides any text that could be a name, classify as PROVIDE_NAME
        - If in COLLECTING_TYPE state and user mentions any kind of project type, classify as PROVIDE_TYPE
        - If in COLLECTING_FEATURES state and user describes functionality, classify as PROVIDE_FEATURES

        Respond with ONLY the intent name, nothing else."""

        context_prompt = f"Message: {message}\nCurrent bot state: {current_state}\n\nWhat is the user's intent?"
        
        try:
            intent_str = self.ai.get_response(context_prompt, system_prompt).strip().upper()
            try:
                return Intent[intent_str]
            except KeyError:
                logger.warning(f"AI returned invalid intent: {intent_str}")
                return Intent.UNKNOWN
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return Intent.UNKNOWN

    def extract_project_type(self, message):
        """Extract and validate project type from message"""
        system_prompt = """You are a project type classifier.
        Analyze the message and extract the main project type (e.g., website, API, CLI tool, mobile app).
        If no clear project type is found, respond with UNKNOWN.
        Respond with ONLY the project type in lowercase, nothing else.
        
        Examples:
        - "website" -> "website"
        - "I want to build a website" -> "website"
        - "make it a CLI tool" -> "cli tool"
        - "random text" -> "unknown"
        """

        try:
            return self.ai.get_response(message, system_prompt).strip().lower()
        except Exception as e:
            logger.error(f"Error extracting project type: {str(e)}")
            return None

    def validate_features(self, features):
        """Validate and analyze project features"""
        system_prompt = """You are a project requirements analyzer.
        Analyze the provided features/requirements and determine if they are clear and specific enough.
        
        Guidelines:
        - VALID: Requirements are clear, specific, and actionable
        - UNCLEAR: Requirements need more details or clarification
        - INVALID: Requirements are problematic or not feasible
        
        Respond with ONLY one of these values (VALID, UNCLEAR, INVALID), nothing else.
        
        Examples:
        - "Show hello world in HTML page" -> VALID
        - "Make it good" -> UNCLEAR
        - "It should do everything" -> INVALID
        """

        try:
            result = self.ai.get_response(features, system_prompt).strip().upper()
            return result in ['VALID', 'UNCLEAR', 'INVALID'], result
        except Exception as e:
            logger.error(f"Error validating features: {str(e)}")
            return False, 'INVALID'