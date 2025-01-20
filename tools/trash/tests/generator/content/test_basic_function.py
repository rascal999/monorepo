"""
Tests for basic test function generation.
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
    generator.add_fixture(
        name="user_data",
        var_type="dynamic",
        scope="function",
        docstring="User data from response",
    )
    return generator


def test_generate_test_function(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating a test function."""
    request_details = {
        "method": "GET",
        "url": {"raw": "/users/{{user_id}}"},
        "sets": ["user_data"],
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{user_id}}"}
        }
    }

    function_lines = content_generator._generate_test_function(
        name="test_get_user",
        request_details=request_details,
        dependencies=["test_create_user"],
        variables=["user_id"],
        fixture_generator=fixture_generator
    )

    # Check function definition
    assert '@pytest.mark.dependency(depends=["test_create_user"])' in function_lines
    assert (
        "def test_get_user(auth_session, env_url, tls_verify, user_id):"
        in function_lines
    )

    # Debug output
    print("\nGenerated function lines:")
    print("\n".join(function_lines))

    # Check request setup
    assert '    method = "GET"' in function_lines
    assert '    url = f"{env_url}/users/{user_id}"' in function_lines

    # Check response handling
    assert any(
        line.strip().startswith("response = auth_session.request(")
        for line in function_lines
    )
    assert any(
        line.strip() == "assert response.status_code == 200" for line in function_lines
    )
