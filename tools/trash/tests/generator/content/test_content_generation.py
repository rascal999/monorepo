"""
Tests for complete test content generation.
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


@pytest.fixture
def sample_collection() -> Dict[str, Any]:
    """Create sample collection."""
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
                                "raw": '{"username": "test", "password": "test"}'
                            }
                        }
                    }
                ]
            },
            {
                "name": "Users",
                "item": [
                    {
                        "name": "Get User",
                        "request": {
                            "method": "GET",
                            "url": {"raw": "/users/{{user_id}}"},
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{token}}"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_dependencies() -> Dict[str, Any]:
    """Create sample dependencies."""
    return {
        "POST /auth/login": {
            "sets": ["token"]
        },
        "POST /users": {
            "sets": ["user_id"]
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

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify imports and configuration
    assert "import pytest" in content
    assert "import requests" in content
    assert "import base64" in content
    assert "from typing import Dict, Any" in content

    # Verify auth fixture
    assert "@pytest.fixture(scope='session')" in content
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


def test_generate_test_with_multiple_dependencies(
    content_generator: ContentGenerator,
    fixture_generator: FixtureGenerator,
):
    """Test generating test with multiple dependencies."""
    request_details = {
        "name": "Get User Orders",
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{user_id}}/orders/{{order_id}}"},
            "header": [
                {
                    "key": "Authorization",
                    "value": "Bearer {{token}}"
                }
            ]
        }
    }

    dependencies = [
        {
            "endpoint": "POST /auth/login",
            "request": {
                "method": "POST",
                "url": {"raw": "/auth/login"},
                "body": {"mode": "raw", "raw": '{"username": "test", "password": "test"}'}
            },
            "sets": ["token"]
        },
        {
            "endpoint": "POST /users",
            "request": {
                "method": "POST",
                "url": {"raw": "/users"},
                "body": {"mode": "raw", "raw": '{"name": "Test User"}'}
            },
            "sets": ["user_id"]
        },
        {
            "endpoint": "POST /orders",
            "request": {
                "method": "POST",
                "url": {"raw": "/orders"},
                "body": {"mode": "raw", "raw": '{"product": "Test Product"}'}
            },
            "sets": ["order_id"]
        }
    ]

    variables = {
        "token": ["POST /auth/login"],
        "user_id": ["POST /users"],
        "order_id": ["POST /orders"]
    }

    content = content_generator.generate_test_content(
        request_details, dependencies, variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify dependency handling
    assert "def test_test_post_auth_login" in content
    assert "def test_test_post_users" in content
    assert "def test_test_post_orders" in content
    assert "def test_test_get_user_orders" in content

    # Verify dependency order
    content_lines = content.split("\n")
    login_index = next(i for i, line in enumerate(content_lines) if "def test_test_post_auth_login" in line)
    users_index = next(i for i, line in enumerate(content_lines) if "def test_test_post_users" in line)
    orders_index = next(i for i, line in enumerate(content_lines) if "def test_test_post_orders" in line)
    main_index = next(i for i, line in enumerate(content_lines) if "def test_test_get_user_orders" in line)

    assert login_index < users_index < orders_index < main_index
