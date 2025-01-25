import logging
from services.core.state_machine import State, StateMachine
from services.project.project_creator import ProjectCreator
from services.project.project_validator import ProjectValidator
from services.core.intent_service import IntentService, Intent
from .project_flow_messages import ProjectFlowMessages

logger = logging.getLogger('orchai.bot.pm.flow')

class ProjectFlowService:
    def __init__(self, ai_service, git_service, message_service):
        self.state_machine = StateMachine()
        self.messages = ProjectFlowMessages(message_service)
        self.validator = ProjectValidator(ai_service, message_service)
        self.creator = ProjectCreator(git_service, ai_service, message_service)
        self.intent_service = IntentService(ai_service)
        
        self.project_requirements = {}
        self.dev_bot = None

    def set_dev_bot(self, dev_bot):
        """Set reference to dev bot configuration"""
        logger.debug("Setting Dev bot reference")
        self.creator.set_dev_bot(dev_bot)
        self.dev_bot = dev_bot

    def handle_project_flow(self, msg_text, username=None):
        """Handle the project creation flow using AI-driven state transitions"""
        if username:
            self.messages.set_user(username)

        try:
            intent = self.intent_service.detect_intent(msg_text, self.state_machine.current_state)
            logger.debug(f"Detected intent: {intent} for message: {msg_text}")
            
            # Handle global intents first
            if self._handle_global_intent(intent, msg_text):
                return

            # Handle state-specific transitions
            self._handle_state_transition(intent, msg_text)

        except Exception as e:
            logger.error(f"Error in project flow: {str(e)}")
            self._handle_error()

    def _handle_global_intent(self, intent, msg_text):
        """Handle intents that can occur in any state"""
        if intent == Intent.CANCEL:
            self._reset_state("Project creation cancelled. Let me know when you want to start again!")
            return True
            
        if intent == Intent.HELP:
            self.messages.send_help_message(self.state_machine.current_state)
            return True
            
        if intent == Intent.BACK:
            new_state = self.state_machine.go_back()
            self.messages.send_state_message(new_state)
            return True
            
        return False

    def _handle_state_transition(self, intent, msg_text):
        """Handle state-specific transitions based on intent"""
        current_state = self.state_machine.current_state

        if current_state == State.IDLE:
            if intent == Intent.CREATE_PROJECT:
                self._transition_to(State.COLLECTING_TYPE)
            else:
                self.messages.send_state_message(State.IDLE)

        elif current_state == State.COLLECTING_TYPE:
            if intent == Intent.PROVIDE_TYPE:
                project_type = self.intent_service.extract_project_type(msg_text)
                if project_type and project_type != "unknown":
                    self.project_requirements['type'] = project_type
                    self._transition_to(State.COLLECTING_NAME)
                else:
                    self.messages.send_error_message('unclear_type')

        elif current_state == State.COLLECTING_NAME:
            # Handle project name directly, regardless of intent
            valid_name, validated_name = self.validator.validate_name(msg_text)
            if valid_name:
                self.project_requirements['name'] = validated_name
                self._transition_to(State.COLLECTING_FEATURES)
            else:
                self.messages.send_error_message('invalid_name')

        elif current_state == State.COLLECTING_FEATURES:
            if intent == Intent.PROVIDE_FEATURES:
                self.project_requirements['features'] = msg_text
                self._transition_to(State.ANALYZING_REQUIREMENTS)
                self._analyze_requirements()
            else:
                # Treat any non-command input as features
                self.project_requirements['features'] = msg_text
                self._transition_to(State.ANALYZING_REQUIREMENTS)
                self._analyze_requirements()

        elif current_state == State.CONFIRMING:
            self._handle_confirmation(intent)

    def _handle_confirmation(self, intent):
        """Handle user response in confirmation state"""
        if intent == Intent.CONFIRM:
            self._transition_to(State.CREATING_PROJECT)
            self._create_project()
        elif intent == Intent.DENY:
            self.messages.send_message("No problem, let's start over.")
            self._transition_to(State.COLLECTING_TYPE)
        elif intent == Intent.EDIT_TYPE:
            self._transition_to(State.COLLECTING_TYPE)
        elif intent == Intent.EDIT_NAME:
            self._transition_to(State.COLLECTING_NAME)
        elif intent == Intent.EDIT_FEATURES:
            self._transition_to(State.COLLECTING_FEATURES)

    def _analyze_requirements(self):
        """Analyze project requirements using AI"""
        is_valid, result = self.intent_service.validate_features(self.project_requirements['features'])
        
        if is_valid and result == 'VALID':
            self._transition_to(State.CONFIRMING)
            self.messages.show_confirmation(self.project_requirements)
        elif result == 'UNCLEAR':
            self.messages.send_error_message('unclear_requirements')
            self._transition_to(State.COLLECTING_FEATURES)
        else:
            self.messages.send_error_message('invalid_requirements')
            self._transition_to(State.COLLECTING_FEATURES)

    def _create_project(self):
        """Create the project and delegate to dev bot"""
        try:
            success = self.creator.create_project(
                self.project_requirements['name'],
                f"Project Type: {self.project_requirements['type']}\n\n"
                f"Features:\n{self.project_requirements['features']}",
                self.messages.current_user
            )
            
            if success:
                self._transition_to(State.HANDOFF_TO_DEV)
                self._reset_state()
            else:
                self.messages.send_error_message('creation_failed')
                self._transition_to(State.COLLECTING_TYPE)

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            self._handle_error()

    def _transition_to(self, new_state):
        """Handle state transitions and messages"""
        self.state_machine.transition_to(new_state)
        self.messages.send_state_message(new_state)

    def _handle_error(self):
        """Handle errors and manage error state"""
        if self.state_machine.handle_error():
            self.messages.send_error_message('max_errors')
            self._reset_state()
        else:
            self.messages.send_error_message('general_error')

    def _reset_state(self):
        """Reset the service's state"""
        logger.debug("Resetting service state")
        self.state_machine.reset()
        self.project_requirements = {}