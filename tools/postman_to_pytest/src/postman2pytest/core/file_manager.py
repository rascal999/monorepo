"""File management utilities for test generation."""

import logging
import shutil
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class FileManager:
    """Manages file operations for test generation."""

    def __init__(self, output_dir: Path, project_root: Path):
        """Initialize the file manager.
        
        Args:
            output_dir: Directory where test files will be generated
            project_root: Root directory of the project
        """
        self.output_dir = output_dir
        self.project_root = project_root

    def copy_project_files(self) -> None:
        """Copy required project files to the output directory."""
        logger.debug("Starting file copy operations")
        
        # Copy .env file if it exists
        env_file = self.project_root / '.env'
        if env_file.exists():
            target_env = self.output_dir / '.env'
            target_env.write_text(env_file.read_text())
            logger.debug(f"Copied project .env file from {env_file} to: {target_env}")
            
        # Copy auth.py to generated tests
        auth_file = self.project_root / 'src' / 'postman2pytest' / 'auth' / 'auth.py'
        target_auth = self.output_dir / 'auth.py'
        target_auth.write_text(auth_file.read_text())
        logger.debug(f"Copied auth.py to: {target_auth}")

    def copy_variable_registry(self, src_path: Path, dest_path: Path) -> None:
        """Copy variable registry to destination.
        
        Args:
            src_path: Source path of the variable registry
            dest_path: Destination path for the variable registry
        """
        if src_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(src_path.read_text())
            logger.debug(f"Copied variable registry from {src_path} to: {dest_path}")

    def ensure_output_directory(self) -> None:
        """Ensure the output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {self.output_dir}")

    def create_test_file(self, file_path: Path, content: str) -> None:
        """Create a test file with the given content.
        
        Args:
            file_path: Path where the test file should be created
            content: Content to write to the file
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        logger.debug(f"Created test file at: {file_path}")
