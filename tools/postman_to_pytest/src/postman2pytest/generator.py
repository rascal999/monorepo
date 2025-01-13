"""Generator module for creating pytest files from Postman collections."""

import json
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
        logger.debug("Starting file copy operations")
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
        logger.debug("Creating conftest.py with shared fixtures")
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
log_path = Path(__file__).resolve().parent.parent / 'test_responses.log'  # Put log in generated_tests root
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()  # Also log to console
    ]
)
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


@pytest.fixture
def resolve_variable(variable_registry):
    """Resolve variables from registry based on their source."""
    from faker import Faker
    fake = Faker()
    
    def _resolve(var_name: str) -> str:
        logger.debug(f"Resolving variable: {var_name}")
        
        if var_name not in variable_registry:
            # Try environment variable if not in registry
            env_value = os.getenv(var_name)
            if env_value:
                logger.debug(f"Found {var_name} in environment: {env_value}")
                return env_value
            raise ValueError(f"Variable {var_name} not found in registry or environment")
            
        var_data = variable_registry[var_name]
        source = var_data.get('source')
        logger.debug(f"Variable {var_name} has source type: {source}")
        
        if source == 'value':
            value = var_data.get('value', '')
            logger.debug(f"Using value source for {var_name}: {value}")
            return value
        elif source == 'random' and var_data.get('faker_method'):
            faker_method = getattr(fake, var_data['faker_method'])
            value = str(faker_method())
            logger.debug(f"Generated random value for {var_name}: {value}")
            return value
        elif source == 'fixture':
            # Try environment variable first for fixture-type variables
            env_value = os.getenv(var_name)
            if env_value:
                logger.debug(f"Found fixture {var_name} in environment: {env_value}")
                return env_value
                
            # Check if we have a response pattern to extract value
            response_pattern = var_data.get('response_pattern')
            if response_pattern:
                logger.debug(f"Attempting to extract {var_name} using pattern: {response_pattern['regex']}")
                
                # Log dependency info
                if 'source_test' in response_pattern:
                    source_test = response_pattern['source_test']
                    source_file = response_pattern.get('source_file', 'unknown')
                    logger.debug(f"Variable {var_name} depends on test {source_test} in {source_file}")
                
                # Search through pytest log for matching response data
                log_path = Path(__file__).resolve().parent.parent / 'test_responses.log'  # Put log in generated_tests root
                if log_path.exists():
                    log_content = log_path.read_text()
                    import re
                    pattern = response_pattern['regex']
                    matches = re.finditer(pattern, log_content)
                    # Get the last match (most recent)
                    match = None
                    for match in matches:
                        pass
                    if match:
                        value = match.group(int(response_pattern['group']))
                        logger.debug(f"Extracted value for {var_name} from response: {value}")
                        return value
                    else:
                        logger.debug(f"No match found for {var_name} in response data")
                else:
                    logger.debug(f"No test_responses.log found for response extraction")
                        
            # Fall back to value or env var
            value = var_data.get('value') or os.getenv(var_name.upper(), '')
            logger.debug(f"Using fallback value for {var_name}: {value}")
            return value
        else:
            # Try environment variable as fallback
            value = os.getenv(var_name, f"{{{var_name}}}")
            logger.debug(f"Using environment fallback for {var_name}: {value}")
            return value
    
    return _resolve
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

        test_content = (
            generate_test_function(
                item,
                url_formatter=format_url,
                sanitize_func=sanitize_name,
                variable_extractor=extract_variables,
                variable_registry=variable_registry,
                auth_config=auth_config,
                version=version,
                client_id=client_id
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
        logger.debug(f"Processing {len(items)} items")
        all_variables = {}
        
        for item in items:
            if isinstance(item, PostmanItem) and item.request:
                logger.debug(f"Processing request item: {item.name}")
                file_path = create_test_file_path(self.output_dir, item)
                self._write_test_file(item, file_path, auth_config)
                
                # Collect variables from this request
                request_vars = collect_variables_from_request(item)
                logger.debug(f"Collected {len(request_vars)} variables from request {item.name}")
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
        logger.info(f"Starting test generation for collection: {collection.info.name if hasattr(collection.info, 'name') else 'Unnamed'}")
        logger.debug(f"Starting test generation for collection with {len(collection.item)} items")
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract auth config from collection if not provided
            if not auth_config and hasattr(collection, 'auth'):
                auth_config = self.auth_handler.extract_auth_config(collection.auth)
                logger.debug(f"Extracted auth config from collection: {auth_config}")
            
            # Process all items in the collection and collect variables
            logger.info("Processing collection items and collecting variables")
            self.variables = self._process_items(collection.item, auth_config)
            logger.debug(f"Collected total of {len(self.variables)} variables from collection")
            
            # Generate variable registry if it doesn't exist
            # Generate variable registry in tools/postman_to_pytest if it doesn't exist
            registry_path = self.project_root / 'variable_registry.json'
            logger.info(f"Generating/updating variable registry at: {registry_path}")
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
                    logger.info(f"Generating new environment file at: {env_path}")
                    generate_env_file(self.variables, env_path)
                    logger.debug(f"Generated environment file: {env_path}")
            
            logger.info("Test generation completed successfully")
            logger.debug(f"Generated tests directory structure at: {self.output_dir}")
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
