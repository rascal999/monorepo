import logging
from enum import Enum, auto

logger = logging.getLogger('orchai.bot.pm.state')

class State(Enum):
    IDLE = auto()
    COLLECTING_TYPE = auto()
    COLLECTING_NAME = auto()
    COLLECTING_FEATURES = auto()
    ANALYZING_REQUIREMENTS = auto()
    CONFIRMING = auto()
    CREATING_PROJECT = auto()
    ERROR_HANDLING = auto()
    HANDOFF_TO_DEV = auto()

class StateMachine:
    def __init__(self):
        self.current_state = State.IDLE
        self.previous_state = None
        self.error_count = 0

    def transition_to(self, new_state):
        """Handle state transitions"""
        logger.debug(f"Transitioning from {self.current_state} to {new_state}")
        self.previous_state = self.current_state
        self.current_state = new_state
        return new_state

    def go_back(self):
        """Return to previous state if available"""
        if self.previous_state:
            return self.transition_to(self.previous_state)
        return self.current_state

    def handle_error(self):
        """Handle error state and count"""
        self.error_count += 1
        if self.error_count >= 3:
            self.reset()
            return True
        self.transition_to(State.ERROR_HANDLING)
        return False

    def reset(self):
        """Reset state machine to initial state"""
        self.current_state = State.IDLE
        self.previous_state = None
        self.error_count = 0