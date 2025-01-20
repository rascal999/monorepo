"""
Tests for import statement generation.
"""

import pytest
from typing import Dict, Any
from src.generator.test import ContentGenerator
from src.generator.handlers.fixtures import FixtureGenerator
from src.utils.auth import AuthManager


@pytest.fixture
def auth_manager() -> AuthManager:
    """Create auth manager for testing."""
    class MockAuthManager:
        oauth_token_url = "https://auth.example.com/token"
        basic_auth_username = "test_client"
        basic_auth_password = "test_secret"
    return MockAuthManager()


@pytest.fixture
def content_generator(auth_manager: AuthManager) -> ContentGenerator:
    """Create test content generator."""
    return ContentGenerator(auth_manager)


def test_generate_imports(content_generator: ContentGenerator):
    """Test generating import statements."""
    import_lines = "\n".join(content_generator._generate_imports())

    # Check essential imports
    assert "import pytest" in import_lines
    assert "import requests" in import_lines
    assert "import base64" in import_lines
    assert "import os" in import_lines
    assert "from typing import Dict, Any" in import_lines

    # Check environment variable imports
    assert 'ENV_URL = os.getenv("ENV_URL")' in import_lines
    assert 'CLIENT_ID = os.getenv("CLIENT_ID")' in import_lines
    assert "_variable_store: Dict[str, Any] = {}" in import_lines


def test_generate_test_with_env_variables(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test content with environment and dynamic variables."""
    request_details = {
        "name": "View User",
        "request": {
            "method": "GET",
            "url": {"raw": "/v2.01/{{CLIENT_ID}}/users/{{USER_LEGAL_OWNER}}"},
        },
    }

    # Add dependency that sets USER_LEGAL_OWNER
    dependencies = [{
        "endpoint": "Create a Legal User (Owner)",
        "request": {
            "method": "POST",
            "url": {"raw": "/v2.01/{{CLIENT_ID}}/users/legal"},
        },
        "sets": ["USER_LEGAL_OWNER"]
    }]

    # Map variables to their setting endpoints
    variables = {"USER_LEGAL_OWNER": ["Create a Legal User (Owner)"]}

    content = content_generator.generate_test_content(
        request_details, dependencies, variables, fixture_generator
    )

    # Verify environment variable imports
    assert 'ENV_URL = os.getenv("ENV_URL")' in content
    assert 'CLIENT_ID = os.getenv("CLIENT_ID")' in content
    assert "_variable_store: Dict[str, Any] = {}" in content

    # Verify OAuth imports
    assert "from requests_oauthlib import OAuth2Session" in content
    assert "from oauthlib.oauth2 import BackendApplicationClient" in content

    # Verify URL formatting using both env and dynamic variables
    assert 'url = f"{env_url}/v2.01/{CLIENT_ID}/users/{USER_LEGAL_OWNER}"' in content


def test_generate_imports_with_custom_types(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating imports with custom type hints."""
    request_details = {
        "name": "Create Complex Object",
        "request": {
            "method": "POST",
            "url": {"raw": "/api/objects"},
            "body": {
                "mode": "raw",
                "raw": '{"data": {"type": "ComplexObject", "attributes": {}}}',
            },
        },
    }

    content = content_generator.generate_test_content(
        request_details, [], {}, fixture_generator
    )

    # Verify type imports
    assert "from typing import Dict, Any" in content
    assert "import json" in content  # For handling JSON request bodies
