"""Generator module for creating pytest files from Postman collections."""

import json
import logging
from pathlib import Path
from typing import Union, List, Dict, Optional

from .parser import PostmanCollection, PostmanItem, PostmanItemGroup
from .conftest_generator import create_conftest
from .file_manager import FileManager
from .variable_processor import VariableProcessor
from .test_file_generator import TestFileGenerator
from .url_utils import sanitize_name

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestGenerator:
    """Generate pytest test files from Postman collections."""

    def __init__(self, output_dir: Path, auth_handler=None, env_file: bool = True, project_root: Optional[Path] = None):
        """Initialize the test generator.
        
        Args:
            output_dir: Directory where test files will be generated
            auth_handler: Optional AuthHandler instance for authentication
            env_file: Whether to generate environment files
            project_root: Optional project root directory
        """
        self.output_dir = output_dir
        self.auth_handler = auth_handler
        self.env_file = env_file
        self.project_root = project_root or Path(__file__).parent.parent.parent
        
        # Initialize components
        self.file_manager = FileManager(output_dir, self.project_root)
        self.variable_processor = VariableProcessor(output_dir, self.project_root)
        self.test_file_generator = TestFileGenerator(output_dir, self.project_root)
        
        logger.debug(f"Initialized TestGenerator with output directory: {output_dir}")
        
        # Expose variable_processor for external access
        self.variable_processor = self.variable_processor

    def _process_items(self, items: List[Union[PostmanItem, PostmanItemGroup]], auth_config=None, parent_path: str = "") -> None:
        """Process a list of Postman items recursively.
        
        Args:
            items: List of PostmanItem or PostmanItemGroup objects
            auth_config: Optional authentication configuration
            parent_path: Path of parent folder for nested items
        """
        # First pass: collect variables
        self.variable_processor.variables = self.variable_processor.process_items(items, auth_config)
        
        # Second pass: validate path variables
        self.variable_processor.validate_path_variables(items)
        
        # Third pass: generate test files
        for item in items:
            if isinstance(item, PostmanItem) and item.request:
                # Create folder path from parent folders
                folder_path = parent_path + "/" + sanitize_name(item.name) if parent_path else sanitize_name(item.name)
                self.test_file_generator.generate_test_file(item, auth_config, folder_path)
            elif hasattr(item, 'item') and item.item:
                # Build folder path for nested items
                new_parent = parent_path + "/" + sanitize_name(item.name) if parent_path else sanitize_name(item.name)
                self._process_items(item.item, auth_config, new_parent)

    def generate_tests(self, collection: PostmanCollection, auth_config=None) -> bool:
        """Generate pytest test files from a Postman collection.
        
        Args:
            collection: Parsed PostmanCollection object
            auth_config: Optional authentication configuration
            
        Returns:
            bool: True if generation was successful
            
        Raises:
            Exception: If any error occurs during generation
        """
        logger.info(f"Starting test generation for collection: {collection.info.name if hasattr(collection.info, 'name') else 'Unnamed'}")
        try:
            # Ensure output directory exists
            self.file_manager.ensure_output_directory()
            
            # Create conftest.py
            create_conftest(self.output_dir)
            
            # Copy required files
            self.file_manager.copy_project_files()
            
            # Extract auth config from collection if not provided
            if not auth_config and hasattr(collection, 'auth'):
                auth_config = self.auth_handler.extract_auth_config(collection.auth)
                logger.debug(f"Extracted auth config from collection: {auth_config}")
            
            # Process all items in the collection
            logger.info("Processing collection items")
            self._process_items(collection.item, auth_config)
            
            # Generate variable files
            self.variable_processor.generate_variable_files(
                collection_name=collection.info.name if hasattr(collection.info, 'name') else '',
                collection_version=collection.info.version if hasattr(collection.info, 'version') else '',
                env_file=self.env_file
            )
            
            # Copy variable registry to output directory
            registry_path = self.project_root / 'variable_registry.json'
            dest_registry = self.output_dir / 'variable_registry.json'
            self.file_manager.copy_variable_registry(registry_path, dest_registry)
            
            logger.info("Test generation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during test generation: {str(e)}", exc_info=True)
            raise


def create_test_generator(output_dir: Path) -> TestGenerator:
    """Create a test generator instance.

    Args:
        output_dir: Directory where test files will be generated

    Returns:
        TestGenerator instance
    """
    return TestGenerator(output_dir)
