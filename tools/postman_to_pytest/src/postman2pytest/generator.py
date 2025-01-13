"""Generator module for creating pytest files from Postman collections."""

import logging
import shutil
from pathlib import Path
from typing import Union, List, Dict, Optional

from .parser import PostmanCollection, PostmanItem, PostmanItemGroup
from .url_utils import create_test_file_path, format_url, sanitize_name
from .test_writer import generate_imports, generate_test_function
from .variable_handler import (
    collect_variables_from_request,
    generate_env_file,
    generate_variable_registry,
    copy_variable_registry,
    extract_variables,
    Variable,
    VariableType
)

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
        """
        self.output_dir = output_dir
        self.auth_handler = auth_handler
        self.env_file = env_file
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.variables = {}  # Store all variables found during processing
        logger.debug(f"Initialized TestGenerator with output directory: {output_dir}")
        
        # Create conftest.py in output directory
        self._create_conftest()
        
        # Copy required files
        self._copy_files()

    def _copy_files(self) -> None:
        """Copy required files to generated tests directory."""
        # Copy .env file
        env_file = Path(__file__).parent.parent.parent / '.env'
        if env_file.exists():
            target_env = self.output_dir / '.env'
            target_env.write_text(env_file.read_text())
            logger.debug(f"Copied project .env file from {env_file} to: {target_env}")
            
        # Copy auth.py to generated tests
        auth_file = Path(__file__).parent / 'auth.py'
        target_auth = self.output_dir / 'auth.py'
        target_auth.write_text(auth_file.read_text())
        logger.debug(f"Copied auth.py to: {target_auth}")

    def _create_conftest(self) -> None:
        """Create conftest.py with shared fixtures."""
        conftest_content = '''"""Shared pytest fixtures."""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytest
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenInfo:
    """OAuth token information."""
    def __init__(self, access_token: str, expires_at: float):
        self.access_token = access_token
        self.expires_at = expires_at


@pytest.fixture
def variable_registry():
    """Load and provide variable registry."""
    try:
        # Find generated_tests directory by looking for conftest.py
        current = Path(__file__).parent
        while current.name != 'generated_tests' and current.parent != current:
            current = current.parent
        if current.name == 'generated_tests':
            registry_path = current / 'variable_registry.json'
        else:
            registry_path = Path(__file__).parent / 'variable_registry.json'
        if registry_path.exists():
            return json.loads(registry_path.read_text()).get('variables', {})
    except Exception:
        pass
    return {}


@pytest.fixture(scope='session')
def auth_handler():
    """Create AuthHandler instance."""
    load_dotenv()
    from auth import AuthHandler  # Import from local auth.py
    handler = AuthHandler()
    # Test OAuth token retrieval on startup
    token = handler._get_oauth_token()
    if not token:
        logger.warning("Failed to obtain initial OAuth token")
    return handler


@pytest.fixture
def base_url():
    """Get base URL from environment."""
    url = os.getenv('ENV_URL', 'https://api.example.com')
    # Ensure URL has scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')  # Remove trailing slash for proper joining


@pytest.fixture
def client_id():
    """Get client ID from environment."""
    return os.getenv('CLIENT_ID', 'test-client-id')
'''
        conftest_path = self.output_dir / 'conftest.py'
        conftest_path.parent.mkdir(parents=True, exist_ok=True)
        conftest_path.write_text(conftest_content)
        logger.debug(f"Created conftest.py at: {conftest_path}")

    def _write_test_file(self, item: PostmanItem, file_path: Path, auth_config=None) -> None:
        """Write a test file for a Postman request.
        
        Args:
            item: PostmanItem containing the request
            file_path: Path where the test file should be written
        """
        logger.debug(f"Writing test file for: {item.name}")
        # Generate imports including auth-related ones if needed
        imports = generate_imports()
        if auth_config and self.auth_handler:
            imports += self.auth_handler.generate_auth_fixture(auth_config)

        test_content = (
            imports +
            generate_test_function(
                item,
                url_formatter=format_url,
                sanitize_func=sanitize_name,
                variable_extractor=extract_variables,
                auth_config=auth_config
            )
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(test_content)
        logger.debug(f"Successfully wrote test file: {file_path}")

    def _process_items(self, items: List[Union[PostmanItem, PostmanItemGroup]], auth_config=None) -> Dict[str, Variable]:
        """Process a list of Postman items recursively.
        
        Args:
            items: List of PostmanItem or PostmanItemGroup objects
        """
        all_variables = {}
        
        for item in items:
            if isinstance(item, PostmanItem) and item.request:
                logger.debug(f"Processing request item: {item.name}")
                file_path = create_test_file_path(self.output_dir, item)
                self._write_test_file(item, file_path, auth_config)
                
                # Collect variables from this request
                request_vars = collect_variables_from_request(item)
                all_variables.update(request_vars)
                
            elif hasattr(item, 'item') and item.item:
                logger.debug(f"Processing item group: {item.name}")
                group_vars = self._process_items(item.item, auth_config)
                all_variables.update(group_vars)
        
        return all_variables

    def generate_tests(self, collection: PostmanCollection, auth_config=None) -> bool:
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
            
            # Extract auth config from collection if not provided
            if not auth_config and hasattr(collection, 'auth'):
                auth_config = self.auth_handler.extract_auth_config(collection.auth)
                logger.debug(f"Extracted auth config from collection: {auth_config}")
            
            # Process all items in the collection and collect variables
            self.variables = self._process_items(collection.item, auth_config)
            
            # Generate variable registry if it doesn't exist
            # Generate variable registry in tools/postman_to_pytest if it doesn't exist
            registry_path = self.project_root / 'variable_registry.json'
            generate_variable_registry(
                self.variables,
                registry_path,
                collection_name=collection.info.name if hasattr(collection.info, 'name') else '',
                collection_version=collection.info.version if hasattr(collection.info, 'version') else '',
                overwrite=False
            )
            logger.debug(f"Generated/updated variable registry: {registry_path}")
            
            # Copy variable registry to generated_tests root
            dest_registry = self.output_dir / 'variable_registry.json'
            copy_variable_registry(registry_path, dest_registry)
            logger.debug(f"Copied variable registry to: {dest_registry}")
            
            # Generate environment file if requested and .env doesn't exist
            if self.env_file:
                env_path = self.output_dir / '.env'
                if not env_path.exists():  # Only generate if .env wasn't copied
                    generate_env_file(self.variables, env_path)
                    logger.debug(f"Generated environment file: {env_path}")
            
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
