"""Generator for conftest.py file."""

import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def create_conftest(output_dir: Path) -> None:
    """Create conftest.py with shared fixtures.
    
    Args:
        output_dir: Directory where conftest.py should be created
    """
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


@pytest.fixture(scope='session')
def shared_data():
    """Session-scoped fixture to store shared data between tests."""
    return {}

@pytest.fixture(scope='session')
def store_response_data(shared_data):
    """Store response data for use in dependent tests."""
    def _store(test_name: str, data: dict):
        logger.debug(f"Storing response data for test {test_name}: {data}")
        shared_data[test_name] = data
    return _store

@pytest.fixture(scope='session')
def get_response_data(shared_data):
    """Get stored response data from previous tests."""
    def _get(test_name: str) -> dict:
        data = shared_data.get(test_name)
        logger.debug(f"Retrieved response data for test {test_name}: {data}")
        return data
    return _get

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
    conftest_path = output_dir / 'conftest.py'
    conftest_path.parent.mkdir(parents=True, exist_ok=True)
    conftest_path.write_text(conftest_content)
    logger.debug(f"Created conftest.py at: {conftest_path}")
