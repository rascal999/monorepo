import os
import logging

logger = logging.getLogger('orchai.bot.dev.project')

class ProjectService:
    def __init__(self, git_service, message_service):
        self.git_service = git_service
        self.message_service = message_service

    def initialize_project(self, msg_text, username):
        """Initialize a new project based on specifications"""
        try:
            # Extract project name from message
            if 'initialize project' not in msg_text.lower():
                self.message_service(f"@{username} Invalid project initialization request")
                return

            # Extract project name and specifications
            parts = msg_text.split('initialize project', 1)[1].strip()
            if not parts:
                self.message_service(f"@{username} Missing project name and specifications")
                return

            # Get project name
            project_name = parts.split()[0].strip()
            if not project_name:
                self.message_service(f"@{username} Missing project name")
                return

            # Create repository
            logger.debug(f"Creating repository: {project_name}")
            repo = self.git_service.create_repo(project_name)
            
            # Create initial project structure
            self._create_project_structure(project_name, repo)
            
            # Notify about completion
            self.message_service(f"@{username} Project {project_name} initialized successfully. Created repository and basic structure.")

        except Exception as e:
            logger.error(f"Error initializing project: {str(e)}")
            self.message_service(f"@{username} Error initializing project: {str(e)}")

    def _create_project_structure(self, project_name, repo):
        """Create the initial project structure"""
        repo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'repos',
            project_name
        )

        # Create basic directories
        os.makedirs(os.path.join(repo_path, 'src'), exist_ok=True)
        os.makedirs(os.path.join(repo_path, 'tests'), exist_ok=True)
        os.makedirs(os.path.join(repo_path, 'docs'), exist_ok=True)

        # Create README
        with open(os.path.join(repo_path, 'README.md'), 'w') as f:
            f.write(f"# {project_name}\n\nProject documentation will be added here.\n")

        # Create gitignore
        with open(os.path.join(repo_path, '.gitignore'), 'w') as f:
            f.write("__pycache__/\n*.py[cod]\n*.so\n.env\nnode_modules/\n")

        # Create initial commit
        repo.index.add('*')
        repo.index.commit('Initial project structure')