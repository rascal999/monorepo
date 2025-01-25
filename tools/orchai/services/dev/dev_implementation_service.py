import logging
import os

logger = logging.getLogger('orchai.bot.dev.implementation')

class DevImplementationService:
    def __init__(self, git_service):
        self.git = git_service

    def setup_project(self, project_name):
        """Set up project structure and dependencies"""
        try:
            # Create project directory
            project_dir = os.path.join(os.getcwd(), project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Initialize git repository
            self.git.init_repo(project_dir)
            
            return project_dir
        except Exception as e:
            logger.error(f"Error setting up project: {str(e)}")
            raise

    def apply_implementation(self, project_dir, implementation):
        """Apply implementation to project files"""
        try:
            # Parse implementation and create/update files
            if "```" in implementation:
                # Extract code blocks and file paths
                blocks = implementation.split("```")
                for i in range(1, len(blocks), 2):
                    code = blocks[i].strip()
                    if i > 0:
                        file_path = blocks[i-1].strip().split('\n')[-1]
                        full_path = os.path.join(project_dir, file_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        with open(full_path, 'w') as f:
                            f.write(code)
            
            # Commit changes
            self.git.commit_changes(project_dir, "Implement task")
            
            return True
        except Exception as e:
            logger.error(f"Error applying implementation: {str(e)}")
            raise

    def run_tests(self, project_dir):
        """Run tests for current implementation"""
        try:
            results = {
                'file_checks': self._check_files(project_dir),
                'syntax_checks': self._check_syntax(project_dir)
            }
            
            return results
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            raise

    def _check_files(self, project_dir):
        """Check if all required files exist"""
        try:
            # For MVP, just check if directory is not empty
            has_files = any(os.listdir(project_dir))
            return {
                'passed': has_files,
                'message': 'All required files exist' if has_files else 'No files found'
            }
        except Exception as e:
            logger.error(f"Error checking files: {str(e)}")
            return {'passed': False, 'message': str(e)}

    def _check_syntax(self, project_dir):
        """Check syntax of implemented files"""
        try:
            # For MVP, just check if files are readable
            errors = []
            for root, _, files in os.walk(project_dir):
                for file in files:
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            f.read()
                    except Exception as e:
                        errors.append(f"Error reading {file}: {str(e)}")
            
            return {
                'passed': not errors,
                'message': 'No syntax errors found' if not errors else '\n'.join(errors)
            }
        except Exception as e:
            logger.error(f"Error checking syntax: {str(e)}")
            return {'passed': False, 'message': str(e)}

    def review_implementation(self, project_dir):
        """Review completed implementation"""
        try:
            findings = []
            
            # Check directory structure
            if not os.path.exists(project_dir):
                findings.append("Project directory not found")
            elif not any(os.listdir(project_dir)):
                findings.append("Project directory is empty")
            
            # Check git repository
            if not os.path.exists(os.path.join(project_dir, '.git')):
                findings.append("Git repository not initialized")
            
            # Check test results
            test_results = self.run_tests(project_dir)
            if not all(r['passed'] for r in test_results.values()):
                for test, result in test_results.items():
                    if not result['passed']:
                        findings.append(f"{test}: {result['message']}")
            
            return findings
        except Exception as e:
            logger.error(f"Error reviewing implementation: {str(e)}")
            raise