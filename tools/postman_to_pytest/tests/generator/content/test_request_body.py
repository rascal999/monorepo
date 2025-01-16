"""
Tests for request body handling in test generation.
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

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify request body handling
    assert 'data = {"name": "Test User", "email": "test@example.com"}' in content
    assert "data=data" in content


def test_generate_test_with_json_body(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with JSON request body."""
    request_details = {
        "name": "Update User",
        "request": {
            "method": "PUT",
            "url": {"raw": "/users/{{user_id}}"},
            "body": {
                "mode": "raw",
                "raw": '{"name": "{{name}}", "email": "{{email}}"}',
            },
        },
    }

    variables = {
        "name": ["Set Name"],
        "email": ["Set Email"]
    }

    content = content_generator.generate_test_content(
        request_details, [], variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify request body handling with variables
    assert 'data = {"name": name, "email": email}' in content
    assert "data=data" in content


def test_generate_test_with_form_data(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test generating test function with form data."""
    request_details = {
        "name": "Upload File",
        "request": {
            "method": "POST",
            "url": {"raw": "/files/upload"},
            "body": {
                "mode": "formdata",
                "formdata": [
                    {
                        "key": "file",
                        "type": "file",
                        "src": "{{file_path}}"
                    },
                    {
                        "key": "description",
                        "value": "{{description}}"
                    }
                ]
            },
        },
    }

    variables = {
        "file_path": ["Set File Path"],
        "description": ["Set Description"]
    }

    content = content_generator.generate_test_content(
        request_details, [], variables, fixture_generator
    )

    # Debug output
    print("\nGenerated content:")
    print(content)

    # Verify form data handling
    assert "files = {'file': open(file_path, 'rb')}" in content
    assert "data = {'description': description}" in content
    assert "files=files" in content
    assert "data=data" in content
