import logging
from .dev_state_machine import DevState

logger = logging.getLogger('orchai.bot.dev.messages')

class DevFlowMessages:
    STATE_MESSAGES = {
        DevState.IDLE: "I'm ready to help with development tasks.",
        DevState.ANALYZING_SPECS: "Analyzing project specifications...",
        DevState.ANALYZING_TASK: "Analyzing task requirements...",
        DevState.PLANNING: "Creating implementation plan...",
        DevState.RESOLVING_DEPENDENCIES: "Setting up project dependencies...",
        DevState.IMPLEMENTING: "Implementing project features...",
        DevState.TESTING: "Running tests and validations...",
        DevState.FIXING_ISSUES: "Addressing implementation issues...",
        DevState.REVIEWING: "Reviewing completed work...",
        DevState.REQUEST_CLARIFICATION: None,  # Uses request_clarification
        DevState.ERROR: "I encountered an issue. Let me try to resolve it.",
        DevState.COMPLETE: None,  # Uses show_completion
    }

    ERROR_MESSAGES = {
        'unclear_specs': "I need more clarity on the project specifications. Could you provide more details?",
        'invalid_specs': "The project specifications seem invalid or incomplete. Please review and update them.",
        'dependency_error': "I encountered issues with project dependencies. Let me try to resolve them.",
        'implementation_error': "There was an error during implementation. I'll try to fix it.",
        'test_failure': "Some tests have failed. I'll investigate and fix the issues.",
        'review_issues': "I found some issues during review that need to be addressed.",
        'max_errors': "I'm having persistent issues. Let's start fresh with clearer requirements.",
        'general_error': "I encountered an error. Let me try to recover."
    }

    def __init__(self, message_service):
        self.message_service = message_service
        self.current_user = None

    def set_user(self, username):
        """Set current user for message context"""
        self.current_user = username

    def send_state_message(self, state):
        """Send message for current state"""
        if message := self.STATE_MESSAGES.get(state):
            self.send_message(message)

    def send_error_message(self, error_type):
        """Send error message by type"""
        if message := self.ERROR_MESSAGES.get(error_type):
            self.send_message(message)

    def request_clarification(self, question):
        """Request clarification about specific aspect"""
        self.send_message(f"I need some clarification: {question}")

    def show_task_progress(self, task, progress):
        """Show progress on current task"""
        self.send_message(f"Progress on {task}: {progress}")

    def show_completion(self, project_name, tasks_completed):
        """Show project/task completion details"""
        completion_msg = (
            f"I've completed the implementation for {project_name}.\n\n"
            f"Completed tasks:\n"
        )
        for task in tasks_completed:
            completion_msg += f"✓ {task}\n"
        
        completion_msg += "\nThe project is ready for review."
        self.send_message(completion_msg)

    def show_implementation_plan(self, plan):
        """Show implementation plan"""
        plan_msg = "Here's my implementation plan:\n\n"
        for i, step in enumerate(plan, 1):
            plan_msg += f"{i}. {step}\n"
        self.send_message(plan_msg)

    def show_test_results(self, results):
        """Show test results"""
        results_msg = "Test Results:\n\n"
        for test, result in results.items():
            status = "✓" if result['passed'] else "✗"
            results_msg += f"{status} {test}: {result['message']}\n"
        self.send_message(results_msg)

    def show_review_findings(self, findings):
        """Show code review findings"""
        if not findings:
            self.send_message("Code review complete. No issues found.")
            return

        review_msg = "Code Review Findings:\n\n"
        for finding in findings:
            review_msg += f"- {finding}\n"
        self.send_message(review_msg)

    def send_message(self, msg):
        """Send a message with proper @username prefix"""
        if self.current_user:
            self.message_service(f"@{self.current_user} {msg}")
        else:
            self.message_service(msg)