"""Test file generation utilities."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional

from .parser import PostmanItem
from .url_utils import create_test_file_path, format_url, sanitize_name
from ..test_generation.test_writer import generate_test_function

# Configure logging
logger = logging.getLogger(__name__)

class TestFileGenerator:
    """Generates pytest test files from Postman requests."""

    def __init__(self, output_dir: Path, project_root: Path):
        """Initialize the test file generator.
        
        Args:
            output_dir: Directory where test files will be generated
            project_root: Root directory of the project
        """
        self.output_dir = output_dir
        self.project_root = project_root

    def generate_test_file(self, item: PostmanItem, auth_config=None, folder_path: str = "") -> Path:
        """Generate a test file for a Postman request.
        
        Args:
            item: PostmanItem containing the request
            auth_config: Optional authentication configuration
            folder_path: Optional folder path for nested items
            
        Returns:
            Path to the generated test file
        """
        logger.debug(f"Generating test file for: {item.name}")
        
        # Extract stable path components for directory structure
        path_parts = []
        if hasattr(item.request.url, 'path') and item.request.url.path:
            # Filter out variable placeholders and keep stable components
            for part in item.request.url.path:
                if not (part.startswith('{{') and part.endswith('}}')):
                    path_parts.append(sanitize_name(part))

        # Create test file path
        method = item.request.method.lower()
        name = sanitize_name(item.name)
        filename = f"test_{method}_{name}.py"
        
        # Build directory path based on stable components
        dir_path = self.output_dir
        for part in path_parts:
            dir_path = dir_path / part
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / filename
        
        # Load variable registry if it exists
        registry_path = self.project_root / 'variable_registry.json'
        variable_registry = {}
        if registry_path.exists():
            try:
                variable_registry = json.loads(registry_path.read_text())
            except Exception as e:
                logger.warning(f"Failed to load variable registry: {e}")

        # Extract version and client_id from file path
        parts = file_path.relative_to(self.output_dir).parts
        version = parts[0] if len(parts) > 0 else None
        client_id = parts[1] if len(parts) > 1 else None

        # Generate test content
        test_content = generate_test_function(
            item,
            url_formatter=format_url,
            sanitize_func=sanitize_name,
            variable_registry=variable_registry,
            auth_config=auth_config,
            version=version,
            client_id=client_id
        )
        
        # Create test file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(test_content)
        logger.debug(f"Successfully wrote test file: {file_path}")
        
        return file_path
