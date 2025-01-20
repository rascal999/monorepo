"""
Tests for complete test file content generation.
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


@pytest.fixture
def fixture_generator() -> FixtureGenerator:
    """Create fixture generator."""
    generator = FixtureGenerator()
    # Add auth_session fixture with tls_verify dependency
    generator.add_fixture(
        name="auth_session",
        var_type="static",
        scope="function",
        dependencies=["tls_verify"],
        docstring="Session with auth token",
    )
    # Add user_data fixture
    generator.add_fixture(
        name="user_data",
        var_type="dynamic",
        scope="function",
        docstring="User data from response",
    )
    return generator


@pytest.fixture
def sample_collection() -> Dict[str, Any]:
    """Create sample Postman collection."""
    return {
        "item": [
            {
                "name": "Auth",
                "item": [
                    {
                        "name": "Login",
                        "request": {
                            "method": "POST",
                            "url": {"raw": "/auth/login"},
                            "body": {
                                "mode": "raw",
                                "raw": '{"username": "test", "password": "test"}',
                            },
                        },
                    }
                ],
            },
            {
                "name": "Users",
                "item": [
                    {
                        "name": "Get User",
                        "request": {
                            "method": "GET",
                            "url": {"raw": "/users/{{user_id}}"},
                        },
                    }
                ],
            },
        ]
    }


@pytest.fixture
def sample_dependencies() -> Dict[str, Any]:
    """Create sample dependencies configuration."""
    return {
        "endpoints": {
            "GET /users/{id}": {
                "dependencies": ["POST /auth/login"],
                "variables": {
                    "token": {"from": "POST /auth/login", "type": "dynamic"},
                },
            }
        }
    }


def test_generate_test_content(
    content_generator: ContentGenerator,
    fixture_generator: FixtureGenerator,
    sample_collection: Dict[str, Any],
    sample_dependencies: Dict[str, Any],
):
    """Test generating complete test file content."""
    # Get request details from sample collection
    request = {
        "name": "Get User",
        "request": next(
            item["request"]
            for folder in sample_collection["item"]
            for item in folder["item"]
            if item["name"] == "Get User"
        ),
    }

    # Get dependencies from sample dependencies
    dependencies = [
        {
            "endpoint": "POST /auth/login",
            "request": next(
                item["request"]
                for folder in sample_collection["item"]
                for item in folder["item"]
                if item["name"] == "Login"
            ),
            "sets": ["token"],
        }
    ]

    # Get variables from dependencies
    variables = {"token": ["POST /auth/login"], "user_id": ["POST /users"]}

    content = content_generator.generate_test_content(
        request, dependencies, variables, fixture_generator
    )

    # Verify imports and configuration
    assert "import pytest" in content
    assert "import requests" in content
    assert "import base64" in content
    assert "from typing import Dict, Any" in content

    # Verify auth fixture
    assert "@pytest.fixture(scope='function')" in content
    assert "def auth_session(tls_verify):" in content

    # Verify dependency test
    assert "@pytest.mark.dependency()" in content
    assert "def test_test_post_auth_login" in content

    # Verify main test
    assert "def test_test_get_user" in content
    assert "@pytest.mark.dependency(depends=[" in content

    # Verify request handling
    assert "response = auth_session.request(" in content
    assert "assert response.status_code == 200" in content
