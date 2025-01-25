import logging
from enum import Enum, auto

logger = logging.getLogger('orchai.bot.dev.state')

class DevState(Enum):
    IDLE = auto()
    ANALYZING_SPECS = auto()
    ANALYZING_TASK = auto()
    PLANNING = auto()
    RESOLVING_DEPENDENCIES = auto()
    IMPLEMENTING = auto()
    TESTING = auto()
    FIXING_ISSUES = auto()
    REVIEWING = auto()
    REQUEST_CLARIFICATION = auto()
    ERROR = auto()
    COMPLETE = auto()

class DevStateMachine:
    def __init__(self):
        self.current_state = DevState.IDLE
        self.previous_state = None
        self.error_count = 0
        self.project_context = {}
        self.task_queue = []
        self.implementation_progress = {}

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
        self.transition_to(DevState.ERROR)
        return False

    def reset(self):
        """Reset state machine to initial state"""
        self.current_state = DevState.IDLE
        self.previous_state = None
        self.error_count = 0
        self.project_context = {}
        self.task_queue = []
        self.implementation_progress = {}

    def add_task(self, task):
        """Add task to queue"""
        self.task_queue.append(task)

    def get_next_task(self):
        """Get next task from queue"""
        return self.task_queue.pop(0) if self.task_queue else None

    def update_progress(self, task_id, status):
        """Update implementation progress"""
        self.implementation_progress[task_id] = status

    def set_project_context(self, context):
        """Set project context"""
        self.project_context = context