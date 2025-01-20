"""
Tests for request content generation (body, headers, query params).
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


def test_generate_test_with_request_body(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with request body."""
    request_details = {
        "name": "Create User",
        "request": {
            "method": "POST",
            "url": {"raw": "/users"},
            "body": {
                "mode": "raw",
                "raw": '{"name": "Test User", "email": "test@example.com"}',
            },
        },
    }

    content = content_generator.generate_test_content(
        request_details, [], {}, fixture_generator
    )

    # Verify request body handling
    assert 'data = {"name": "Test User", "email": "test@example.com"}' in content
    assert "data=data" in content


def test_generate_test_with_headers(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with custom headers."""
    request_details = {
        "name": "Get User Details",
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{user_id}}"},
            "header": [
                {
                    "key": "Accept",
                    "value": "application/json"
                },
                {
                    "key": "X-Custom-Header",
                    "value": "{{custom_value}}"
                }
            ]
        }
    }

    variables = {"custom_value": ["Set Custom Value"]}
    content = content_generator.generate_test_content(
        request_details, [], variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify header handling
    assert 'headers = {"Accept": "application/json", "X-Custom-Header": custom_value}' in content


def test_generate_test_with_query_params(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with query parameters."""
    request_details = {
        "name": "Search Users",
        "request": {
            "method": "GET",
            "url": {
                "raw": "/users?page={{page}}&limit={{limit}}",
                "query": [
                    {"key": "page", "value": "{{page}}"},
                    {"key": "limit", "value": "{{limit}}"}
                ]
            }
        }
    }

    variables = {
        "page": ["Set Page"],
        "limit": ["Set Limit"]
    }
    content = content_generator.generate_test_content(
        request_details, [], variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify query parameter handling
    assert 'url = f"{env_url}/users?page={page}&limit={limit}"' in content
