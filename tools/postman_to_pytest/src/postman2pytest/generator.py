"""Generator module for creating pytest files from Postman collections."""

import logging
from pathlib import Path
from typing import Union, List

from .parser import PostmanCollection, PostmanItem, PostmanItemGroup
from .url_utils import create_test_file_path, format_url, sanitize_name
from .test_writer import generate_imports, generate_test_function
from .variable_handler import extract_variables

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestGenerator:
    """Generate pytest test files from Postman collections."""

    def __init__(self, output_dir: Path):
        """Initialize the test generator.
        
        Args:
            output_dir: Directory where test files will be generated
        """
        self.output_dir = output_dir
        logger.debug(f"Initialized TestGenerator with output directory: {output_dir}")

    def _write_test_file(self, item: PostmanItem, file_path: Path) -> None:
        """Write a test file for a Postman request.
        
        Args:
            item: PostmanItem containing the request
            file_path: Path where the test file should be written
        """
        logger.debug(f"Writing test file for: {item.name}")
        test_content = (
            generate_imports() +
            generate_test_function(
                item,
                url_formatter=format_url,
                sanitize_func=sanitize_name,
                variable_extractor=extract_variables
            )
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(test_content)
        logger.debug(f"Successfully wrote test file: {file_path}")

    def _process_items(self, items: List[Union[PostmanItem, PostmanItemGroup]]) -> None:
        """Process a list of Postman items recursively.
        
        Args:
            items: List of PostmanItem or PostmanItemGroup objects
        """
        for item in items:
            if isinstance(item, PostmanItem) and item.request:
                logger.debug(f"Processing request item: {item.name}")
                file_path = create_test_file_path(self.output_dir, item)
                self._write_test_file(item, file_path)
            elif hasattr(item, 'item') and item.item:
                logger.debug(f"Processing item group: {item.name}")
                self._process_items(item.item)

    def generate_tests(self, collection: PostmanCollection) -> bool:
        """Generate pytest test files from a Postman collection.
        
        Args:
            collection: Parsed PostmanCollection object
            
        Returns:
            bool: True if generation was successful
            
        Raises:
            Exception: If any error occurs during generation
        """
        logger.debug(f"Starting test generation for collection with {len(collection.item)} items")
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process all items in the collection
            self._process_items(collection.item)
            
            logger.debug("Test generation completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during test generation: {str(e)}")
            raise


def create_test_generator(output_dir: Path) -> TestGenerator:
    """Create a test generator instance.

    Args:
        output_dir: Directory where test files will be generated

    Returns:
        TestGenerator instance
    """
    return TestGenerator(output_dir)
