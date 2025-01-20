"""
Shared fixtures for generator tests.
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
def sample_collection() -> Dict[str, Any]:
    """Sample Postman collection for testing."""
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
        ],
    }


@pytest.fixture
def sample_dependencies() -> Dict[str, Any]:
    """Sample dependency configuration for testing."""
    return {
        "endpoints": {
            "GET /users/{id}": {
                "dependencies": ["POST /auth/login"],
                "variables": {
                    "token": {"type": "dynamic", "from": "POST /auth/login"},
                },
            },
        },
    }
