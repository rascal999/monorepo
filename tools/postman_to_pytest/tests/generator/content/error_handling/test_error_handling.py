"""
Tests for error handling and assertions in generated tests.
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


def test_generate_test_with_error_handling(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with error handling."""
    request_details = {
        "name": "Delete User",
        "request": {
            "method": "DELETE",
            "url": {"raw": "/users/{{user_id}}"}
        },
        "test": [
            {
                "name": "Status code is 204",
                "assertion": "response.status_code === 204"
            },
            {
                "name": "Response has no content",
                "assertion": "!response.text"
            }
        ]
    }

    content = content_generator.generate_test_content(
        request_details, [], {"user_id": ["Create User"]}, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify error handling
    assert "try:" in content
    assert "except requests.exceptions.RequestException as e:" in content
    assert "pytest.fail" in content

    # Verify assertions
    assert "assert response.status_code == 204" in content
    assert "assert not response.text" in content


def test_generate_test_with_custom_assertions(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with custom assertions."""
    request_details = {
        "name": "Get User Profile",
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{user_id}}/profile"}
        },
        "test": [
            {
                "name": "Status code is 200",
                "assertion": "response.status_code === 200"
            },
            {
                "name": "Response has required fields",
                "assertion": "response.json().name && response.json().email"
            }
        ]
    }

    content = content_generator.generate_test_content(
        request_details, [], {"user_id": ["Create User"]}, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify assertions
    assert "assert response.status_code == 200" in content


def test_generate_test_with_default_assertions(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with default assertions when none specified."""
    request_details = {
        "name": "List Users",
        "request": {
            "method": "GET",
            "url": {"raw": "/users"}
        }
        # No test assertions specified
    }

    content = content_generator.generate_test_content(
        request_details, [], {}, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify default assertion is added
    assert "assert response.status_code == 200" in content
