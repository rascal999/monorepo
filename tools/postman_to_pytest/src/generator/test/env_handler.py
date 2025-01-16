"""Environment file handling utilities."""

import os
from pathlib import Path
from typing import Optional


class EnvHandler:
    """Handles environment file operations."""

    def __init__(self, output_dir: str, base_dir: Optional[str] = None):
        """Initialize environment handler.

        Args:
            output_dir: Output directory for generated tests
            base_dir: Base directory for finding .env files
        """
        self.output_dir = output_dir
        self.base_dir = base_dir or os.getcwd()

    def copy_env_file(self) -> None:
        """Copy environment file to output directory.
        
        Looks for .env file in the following order:
        1. Project root directory
        2. Current/base directory
        3. .env.sample from project root
        """
        output_path = Path(self.output_dir) / ".env"
        
        # Try project root .env
        project_root = Path(self.base_dir).parent
        print(f"Project root: {project_root}")
        root_env = project_root / ".env"
        print(f"Root .env exists: {root_env.exists()}")
        if root_env.exists():
            content = root_env.read_text()
            print(f"Root env content: {content}")
            output_path.write_text(content)
            print(f"Output env content after write: {output_path.read_text()}")
            return

        # Try current/base directory .env
        base_env = Path(self.base_dir) / ".env"
        print(f"Base .env exists: {base_env.exists()}")
        if base_env.exists():
            content = base_env.read_text()
            print(f"Base env content: {content}")
            output_path.write_text(content)
            print(f"Output env content after write: {output_path.read_text()}")
            return

        # Try .env.sample from project root
        sample_env = project_root / ".env.sample"
        print(f"Sample .env exists: {sample_env.exists()}")
        if sample_env.exists():
            print(f"Reading sample content from: {sample_env}")
            sample_content = sample_env.read_text()
            print(f"Sample content: {sample_content}")
            print(f"Writing to output path: {output_path}")
            output_path.write_text(sample_content)
            print(f"Verifying content...")
            written_content = output_path.read_text()
            print(f"Written content: {written_content}")
            print(f"Output env content after write: {output_path.read_text()}")
            assert written_content == sample_content, f"Content mismatch. Expected: {sample_content}, Got: {written_content}"
            return

        print("No env files found, not creating default template")
