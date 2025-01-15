"""
Tests for content generator functionality.
"""

import pytest
from typing import Dict, Any
from unittest.mock import MagicMock
from src.generator.content_generator import ContentGenerator
from src.generator.fixtures import FixtureGenerator
from src.utils.auth import AuthManager


@pytest.fixture
def auth_manager() -> AuthManager:
    """Create auth manager for testing."""
    manager = MagicMock(spec=AuthManager)
    manager.oauth_token_url = "https://api.test.com/oauth/token"
    manager.basic_auth_username = "test_client"
    manager.basic_auth_password = "test_secret"
    return manager


@pytest.fixture
def fixture_generator() -> FixtureGenerator:
    """Create fixture generator with test fixtures."""
    generator = FixtureGenerator()
    generator.add_fixture(
        name="token",
        var_type="dynamic",
        scope="function",
        docstring="Authentication token from login",
    )
    generator.add_fixture(
        name="user_id",
        var_type="dynamic",
        dependencies=["token"],
        docstring="User ID from create user response",
    )
    return generator


@pytest.fixture
def content_generator(auth_manager: AuthManager) -> ContentGenerator:
    """Create content generator for testing."""
    return ContentGenerator(auth_manager)


def test_generate_imports(content_generator: ContentGenerator):
    """Test generating import statements."""
    content = content_generator.generate_test_content(
        request_details={
            "name": "Test Request",
            "request": {
                "method": "GET",
                "url": {"raw": "/test"},
            },
        },
        dependencies=[],
        variables={},
        fixture_generator=FixtureGenerator(),
    )

    # Verify imports
    assert "import pytest" in content
    assert "import requests" in content
    assert "import base64" in content
    assert "import os" in content
    assert "from typing import Dict, Any" in content

    # Verify environment variables
    assert 'ENV_URL = os.getenv("ENV_URL")' in content
    assert 'CLIENT_ID = os.getenv("CLIENT_ID")' in content


def test_generate_auth_config(content_generator: ContentGenerator):
    """Test generating auth configuration."""
    content = content_generator.generate_test_content(
        request_details={
            "name": "Test Request",
            "request": {
                "method": "GET",
                "url": {"raw": "/test"},
            },
        },
        dependencies=[],
        variables={},
        fixture_generator=FixtureGenerator(),
    )

    # Verify auth configuration
    assert 'BASIC_AUTH_USERNAME = "test_client"' in content
    assert 'BASIC_AUTH_PASSWORD = "test_secret"' in content
    assert 'AUTH_TOKEN_URL = "https://api.test.com/oauth/token"' in content

    # Verify auth session fixture
    assert "@pytest.fixture(scope='session')" in content
    assert "def auth_session(tls_verify):" in content
    assert "from requests_oauthlib import OAuth2Session" in content
    assert "from oauthlib.oauth2 import BackendApplicationClient" in content


def test_generate_test_function(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function."""
    content = content_generator.generate_test_content(
        request_details={
            "name": "Get User",
            "request": {
                "method": "GET",
                "url": {"raw": "/users/{{user_id}}"},
                "header": [
                    {"key": "Authorization", "value": "Bearer {{token}}"},
                ],
            },
        },
        dependencies=[
            {
                "endpoint": "POST /auth/login",
                "request": {
                    "method": "POST",
                    "url": {"raw": "/auth/login"},
                },
                "sets": ["token"],
            },
        ],
        variables={"token": ["POST /auth/login"]},
        fixture_generator=fixture_generator,
    )

    # Verify test function
    assert '@pytest.mark.dependency(depends=["test_test_post_auth_login"])' in content
    assert (
        "def test_test_get_user(auth_session, env_url, tls_verify, token):" in content
    )
    assert 'method = "GET"' in content
    assert 'url = f"{env_url}/users/{user_id}"' in content
    assert "response = auth_session.request(" in content
    assert "assert response.status_code == 200" in content


def test_dependency_chain(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test handling dependency chain."""
    content = content_generator.generate_test_content(
        request_details={
            "name": "Get User Details",
            "request": {
                "method": "GET",
                "url": {"raw": "/users/{{user_id}}"},
            },
        },
        dependencies=[
            {
                "endpoint": "POST /auth/login",
                "request": {
                    "method": "POST",
                    "url": {"raw": "/auth/login"},
                },
                "sets": ["token"],
            },
            {
                "endpoint": "POST /users",
                "request": {
                    "method": "POST",
                    "url": {"raw": "/users"},
                },
                "sets": ["user_id"],
            },
        ],
        variables={
            "token": ["POST /auth/login"],
            "user_id": ["POST /users"],
        },
        fixture_generator=fixture_generator,
    )

    # Verify dependency order
    login_pos = content.find("test_test_post_auth_login")
    create_pos = content.find("test_test_post_users")
    get_pos = content.find("test_test_get_user_details")

    assert login_pos < create_pos < get_pos


def test_request_body_handling(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test handling request body."""
    content = content_generator.generate_test_content(
        request_details={
            "name": "Create User",
            "request": {
                "method": "POST",
                "url": {"raw": "/users"},
                "body": {
                    "mode": "raw",
                    "raw": '{"name": "test"}',
                },
            },
        },
        dependencies=[],
        variables={},
        fixture_generator=fixture_generator,
    )

    # Verify request body
    assert 'data = {"name": "test"}' in content
    assert "data=data" in content


def test_variable_handling(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test handling variables in URLs and headers."""
    content = content_generator.generate_test_content(
        request_details={
            "name": "Get User",
            "request": {
                "method": "GET",
                "url": {"raw": "/users/{{user_id}}"},
                "header": [
                    {"key": "Authorization", "value": "Bearer {{token}}"},
                ],
            },
        },
        dependencies=[],
        variables={"user_id": ["POST /users"], "token": ["POST /auth/login"]},
        fixture_generator=fixture_generator,
    )

    # Verify variable usage
    assert "user_id" in content
    assert "token" in content
    assert 'url = f"{env_url}/users/{user_id}"' in content
    assert "Bearer {token}" in content
