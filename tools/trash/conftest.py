"""
Root conftest.py for test configuration and path setup.
"""

import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

@pytest.fixture(scope='session')
def env_url():
    """Get base environment URL."""
    return os.getenv('ENV_URL')

@pytest.fixture(scope='session')
def tls_verify():
    """Get TLS verification setting."""
    return os.getenv('TLS_VERIFY', 'true').lower() == 'true'
