"""
Tests for header handling in test generation.
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
    return FixtureGenerator()


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


def test_generate_test_with_auth_header(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with auth header."""
    request_details = {
        "name": "Get Protected Resource",
        "request": {
            "method": "GET",
            "url": {"raw": "/protected"},
            "header": [
                {
                    "key": "Authorization",
                    "value": "Bearer {{token}}"
                }
            ]
        }
    }

    variables = {"token": ["Get Token"]}
    content = content_generator.generate_test_content(
        request_details, [], variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify auth header handling
    assert 'headers = {"Authorization": f"Bearer {token}"}' in content


def test_generate_test_with_multiple_headers(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with multiple headers."""
    request_details = {
        "name": "Create Resource",
        "request": {
            "method": "POST",
            "url": {"raw": "/resources"},
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json"
                },
                {
                    "key": "Accept",
                    "value": "application/json"
                },
                {
                    "key": "X-Request-ID",
                    "value": "{{request_id}}"
                }
            ]
        }
    }

    variables = {"request_id": ["Set Request ID"]}
    content = content_generator.generate_test_content(
        request_details, [], variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify multiple header handling
    assert 'headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Request-ID": request_id}' in content
