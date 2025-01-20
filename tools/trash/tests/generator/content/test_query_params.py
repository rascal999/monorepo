"""
Tests for query parameter handling in test generation.
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


def test_generate_test_with_static_query_params(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with static query parameters."""
    request_details = {
        "name": "List Users",
        "request": {
            "method": "GET",
            "url": {
                "raw": "/users?status=active&sort=name",
                "query": [
                    {"key": "status", "value": "active"},
                    {"key": "sort", "value": "name"}
                ]
            }
        }
    }

    content = content_generator.generate_test_content(
        request_details, [], {}, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify static query parameter handling
    assert 'url = f"{env_url}/users?status=active&sort=name"' in content


def test_generate_test_with_mixed_query_params(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with mixed static and dynamic query parameters."""
    request_details = {
        "name": "Filter Users",
        "request": {
            "method": "GET",
            "url": {
                "raw": "/users?role=admin&page={{page}}&limit={{limit}}&sort=name",
                "query": [
                    {"key": "role", "value": "admin"},
                    {"key": "page", "value": "{{page}}"},
                    {"key": "limit", "value": "{{limit}}"},
                    {"key": "sort", "value": "name"}
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

    # Verify mixed query parameter handling
    assert 'url = f"{env_url}/users?role=admin&page={page}&limit={limit}&sort=name"' in content
