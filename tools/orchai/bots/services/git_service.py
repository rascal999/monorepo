import os
import logging

logger = logging.getLogger('orchai.bot.git')

class GitService:
    def __init__(self, user_name, user_email):
        self.user_name = user_name
        self.user_email = user_email

    def create_repo(self, repo_name):
        """Create a new repository"""
        try:
            # Create repo directory
            repo_dir = os.path.join('repos', repo_name)
            os.makedirs(repo_dir, exist_ok=True)

            # Initialize git repo
            os.system(f'cd {repo_dir} && git init')
            os.system(f'cd {repo_dir} && git config user.name "{self.user_name}"')
            os.system(f'cd {repo_dir} && git config user.email "{self.user_email}"')

            return repo_dir
        except Exception as e:
            logger.error(f"Error creating repository: {str(e)}")
            raise

    def init_repo(self, repo_dir):
        """Initialize git repository in existing directory"""
        try:
            os.system(f'cd {repo_dir} && git init')
            os.system(f'cd {repo_dir} && git config user.name "{self.user_name}"')
            os.system(f'cd {repo_dir} && git config user.email "{self.user_email}"')
            return True
        except Exception as e:
            logger.error(f"Error initializing repository: {str(e)}")
            raise

    def commit_changes(self, repo_dir, message):
        """Commit changes in repository"""
        try:
            os.system(f'cd {repo_dir} && git add .')
            os.system(f'cd {repo_dir} && git commit -m "{message}"')
            return True
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            raise

    def push_changes(self, repo_dir, branch='main'):
        """Push changes to remote"""
        try:
            os.system(f'cd {repo_dir} && git push origin {branch}')
            return True
        except Exception as e:
            logger.error(f"Error pushing changes: {str(e)}")
            raise