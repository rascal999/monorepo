import logging
from .dev_state_machine import DevState, DevStateMachine
from .dev_flow_messages import DevFlowMessages
from .dev_task_analyzer import DevTaskAnalyzer
from .dev_implementation_service import DevImplementationService

logger = logging.getLogger('orchai.bot.dev.flow')

class DevFlowService:
    def __init__(self, ai_service, git_service, message_service):
        self.state_machine = DevStateMachine()
        self.messages = DevFlowMessages(message_service)
        self.task_analyzer = DevTaskAnalyzer(ai_service)
        self.implementation = DevImplementationService(git_service)

    def handle_project_handoff(self, project_name, specifications, username=None):
        """Handle project handoff from PM bot"""
        if username:
            self.messages.set_user(username)

        try:
            self.state_machine.set_project_context({
                'name': project_name,
                'specs': specifications,
                'tasks_completed': []
            })
            self._transition_to(DevState.ANALYZING_SPECS)
            self._analyze_specifications()
        except Exception as e:
            logger.error(f"Error handling project handoff: {str(e)}")
            self._handle_error()

    def handle_message(self, msg_text, username=None):
        """Handle incoming messages"""
        if username:
            self.messages.set_user(username)

        try:
            if self.state_machine.current_state == DevState.REQUEST_CLARIFICATION:
                self._handle_clarification(msg_text)
            else:
                self._process_message(msg_text)
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            self._handle_error()

    def _analyze_specifications(self):
        """Analyze project specifications"""
        try:
            specs = self.state_machine.project_context['specs']
            tasks = self.task_analyzer.analyze_specifications(specs)
            self.state_machine.task_queue = tasks
            
            self._transition_to(DevState.PLANNING)
            plan = self.task_analyzer.create_implementation_plan(tasks)
            self.messages.show_implementation_plan(plan)
            
            self._transition_to(DevState.RESOLVING_DEPENDENCIES)
            self._setup_project()
        except Exception as e:
            logger.error(f"Error analyzing specifications: {str(e)}")
            self._request_clarification("Could you provide more detailed specifications?")

    def _setup_project(self):
        """Set up project structure and dependencies"""
        try:
            project_name = self.state_machine.project_context['name']
            project_dir = self.implementation.setup_project(project_name)
            self.state_machine.project_context['dir'] = project_dir
            
            self._transition_to(DevState.IMPLEMENTING)
            self._implement_next_task()
        except Exception as e:
            logger.error(f"Error setting up project: {str(e)}")
            self.messages.send_error_message('dependency_error')
            self._handle_error()

    def _implement_next_task(self):
        """Implement next task in queue"""
        try:
            task = self.state_machine.get_next_task()
            if not task:
                self._transition_to(DevState.REVIEWING)
                self._review_implementation()
                return

            self.messages.show_task_progress(task['description'], "Starting")
            
            # Generate implementation
            implementation = self.task_analyzer.generate_implementation(task)
            
            # Apply implementation
            project_dir = self.state_machine.project_context['dir']
            self.implementation.apply_implementation(project_dir, implementation)
            
            self.state_machine.project_context['tasks_completed'].append(task['description'])
            self._transition_to(DevState.TESTING)
            self._run_tests()
        except Exception as e:
            logger.error(f"Error implementing task: {str(e)}")
            self.messages.send_error_message('implementation_error')
            self._transition_to(DevState.FIXING_ISSUES)

    def _run_tests(self):
        """Run tests for current implementation"""
        try:
            project_dir = self.state_machine.project_context['dir']
            results = self.implementation.run_tests(project_dir)
            
            self.messages.show_test_results(results)
            
            if all(r['passed'] for r in results.values()):
                self._implement_next_task()
            else:
                self.messages.send_error_message('test_failure')
                self._transition_to(DevState.FIXING_ISSUES)
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            self._handle_error()

    def _review_implementation(self):
        """Review completed implementation"""
        try:
            project_dir = self.state_machine.project_context['dir']
            findings = self.implementation.review_implementation(project_dir)
            
            if not findings:
                project_name = self.state_machine.project_context['name']
                tasks_completed = self.state_machine.project_context['tasks_completed']
                self.messages.show_completion(project_name, tasks_completed)
                self._transition_to(DevState.COMPLETE)
                self._reset_state()
            else:
                self.messages.show_review_findings(findings)
                self._transition_to(DevState.FIXING_ISSUES)
        except Exception as e:
            logger.error(f"Error reviewing implementation: {str(e)}")
            self._handle_error()

    def _handle_clarification(self, msg_text):
        """Handle clarification response"""
        try:
            previous_state = self.state_machine.previous_state
            self._transition_to(previous_state)
            self._process_message(msg_text)
        except Exception as e:
            logger.error(f"Error handling clarification: {str(e)}")
            self._handle_error()

    def _process_message(self, msg_text):
        """Process incoming message based on current state"""
        try:
            if "error" in msg_text.lower() or "issue" in msg_text.lower():
                self._transition_to(DevState.FIXING_ISSUES)
            elif "test" in msg_text.lower():
                self._transition_to(DevState.TESTING)
                self._run_tests()
            elif "review" in msg_text.lower():
                self._transition_to(DevState.REVIEWING)
                self._review_implementation()
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self._handle_error()

    def _request_clarification(self, question):
        """Request clarification from user"""
        self.state_machine.previous_state = self.state_machine.current_state
        self._transition_to(DevState.REQUEST_CLARIFICATION)
        self.messages.request_clarification(question)

    def _handle_error(self):
        """Handle errors and manage error state"""
        if self.state_machine.handle_error():
            self.messages.send_error_message('max_errors')
            self._reset_state()
        else:
            self.messages.send_error_message('general_error')

    def _transition_to(self, new_state):
        """Handle state transitions and messages"""
        self.state_machine.transition_to(new_state)
        self.messages.send_state_message(new_state)

    def _reset_state(self):
        """Reset the service's state"""
        logger.debug("Resetting service state")
        self.state_machine.reset()