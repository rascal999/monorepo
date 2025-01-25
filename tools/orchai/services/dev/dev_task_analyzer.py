import logging
import json

logger = logging.getLogger('orchai.bot.dev.analyzer')

class DevTaskAnalyzer:
    def __init__(self, ai_service):
        self.ai = ai_service

    def analyze_specifications(self, specs):
        """Analyze project specifications and break down into tasks"""
        try:
            # Extract project name and tasks from markdown
            project_name = None
            tasks = []
            current_task = None

            for line in specs.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if "**Project:" in line:
                    project_name = line.split("**Project:")[1].strip().strip('*')
                elif "**Technical Tasks:**" in line:
                    continue
                elif line.startswith('*'):
                    # This is a task detail
                    if current_task:
                        current_task['details'].append(line.strip('* '))
                elif line.startswith('1.') or line.startswith('2.'):
                    # This is a main task
                    if current_task:
                        tasks.append(current_task)
                    current_task = {
                        'description': line.split('.')[1].strip(),
                        'details': []
                    }

            # Add the last task
            if current_task:
                tasks.append(current_task)

            return tasks
        except Exception as e:
            logger.error(f"Error analyzing specifications: {str(e)}")
            raise

    def create_implementation_plan(self, tasks):
        """Create implementation plan from tasks"""
        try:
            plan = []
            for task in tasks:
                plan.append(f"Task: {task['description']}")
                for detail in task['details']:
                    plan.append(f"  - {detail}")
            return plan
        except Exception as e:
            logger.error(f"Error creating implementation plan: {str(e)}")
            raise

    def generate_implementation(self, task):
        """Generate implementation code for a task"""
        try:
            system_prompt = f"""Implement the following task:
            {task['description']}
            
            Details:
            {json.dumps(task['details'], indent=2)}
            
            Provide the complete implementation code and file paths.
            Use markdown code blocks with file paths as headers."""
            
            return self.ai.get_response(str(task), system_prompt)
        except Exception as e:
            logger.error(f"Error generating implementation: {str(e)}")
            raise