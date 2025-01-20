"""
Main pytest configuration.
"""
import pytest
from postman2pytest.dynamic_vars import (
    dynamic_vars,
    pytest_runtest_call,
    pytest_runtest_makereport
)
from postman2pytest.fixtures import (
    env_vars,
    faker_vars,
    api_session
)

def pytest_configure(config):
    """Configure pytest."""
    # Enable debug logging
    config.option.verbose = True
    # Register dependency marker
    config.addinivalue_line(
        "markers", "dependency(name=None, depends=[]): mark test dependencies"
    )

# Import fixtures and hooks
__all__ = [
    # Dynamic variables
    'dynamic_vars',
    'pytest_runtest_call',
    'pytest_runtest_makereport',
    
    # Test fixtures
    'env_vars',
    'faker_vars',
    'api_session'
]
