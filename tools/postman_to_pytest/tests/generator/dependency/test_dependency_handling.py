"""
Tests for dependency and variable chain handling.
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


def test_simple_dependency_chain(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test handling of simple dependency chain."""
    # Main request
    request = {
        "name": "View a User",
        "request": {
            "method": "GET",
            "url": {"raw": "/v2.01/{{CLIENT_ID}}/users/{{USER_LEGAL_OWNER}}"}
        }
    }

    # Dependencies in specific order
    dependencies = [
        {
            "endpoint": "Create a Legal User (Owner)",
            "request": {
                "method": "POST",
                "url": {"raw": "/v2.01/{{CLIENT_ID}}/users/legal"}
            },
            "sets": ["USER_LEGAL_OWNER"]
        }
    ]

    # Map variables to their setting endpoints
    variables = {"USER_LEGAL_OWNER": ["Create a Legal User (Owner)"]}

    content = content_generator.generate_test_content(
        request, dependencies, variables, fixture_generator
    )

    # Debug output
    print("\n=== Generated Content ===")
    print(content)
    print("\n=== Looking for test functions ===")
    print(f"Looking for: def test_test_create_a_legal_user_owner")
    print(f"Looking for: def test_test_view_a_user")

    # Find positions of test functions
    create_pos = content.find("def test_test_create_a_legal_user_owner")
    view_pos = content.find("def test_test_view_a_user")

    print(f"Found positions - create: {create_pos}, view: {view_pos}")

    # Verify order
    assert create_pos >= 0, "Create test function not found"
    assert view_pos >= 0, "View test function not found"
    assert create_pos < view_pos, "Create test should come before view test"

    # Verify dependency marker
    assert '@pytest.mark.dependency(depends=["test_test_create_a_legal_user_owner"])' in content

    # Verify fixture creation
    assert "@pytest.fixture(scope='function')" in content
    assert "def USER_LEGAL_OWNER():" in content
    assert "_variable_store.get('USER_LEGAL_OWNER')" in content

    # Verify variable storage
    assert "_variable_store['USER_LEGAL_OWNER'] = response" in content


def test_complex_dependency_chain(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test handling of complex dependency chain with multiple variables."""
    # Main request
    request = {
        "name": "View User Wallet",
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{USER_ID}}/wallets/{{WALLET_ID}}"}
        }
    }

    # Dependencies that set variables
    dependencies = [
        {
            "endpoint": "Create User",
            "request": {
                "method": "POST",
                "url": {"raw": "/users"}
            },
            "sets": ["USER_ID"]
        },
        {
            "endpoint": "Create Wallet",
            "request": {
                "method": "POST",
                "url": {"raw": "/users/{{USER_ID}}/wallets"}
            },
            "sets": ["WALLET_ID"],
            "uses_variables": {"USER_ID": {"type": "dynamic"}}
        }
    ]

    # Map variables to their setting endpoints
    variables = {
        "USER_ID": ["Create User"],
        "WALLET_ID": ["Create Wallet"]
    }

    content = content_generator.generate_test_content(
        request, dependencies, variables, fixture_generator
    )

    # Debug output
    print("\n=== Generated Content ===")
    print(content)
    print("\n=== Looking for test functions ===")
    print(f"Looking for: def test_test_create_user")
    print(f"Looking for: def test_test_create_wallet")
    print(f"Looking for: def test_test_view_user_wallet")

    # Find positions of test functions
    create_user_pos = content.find("def test_test_create_user")
    create_wallet_pos = content.find("def test_test_create_wallet")
    view_wallet_pos = content.find("def test_test_view_user_wallet")

    print(f"Found positions - create_user: {create_user_pos}, create_wallet: {create_wallet_pos}, view_wallet: {view_wallet_pos}")

    # Verify order
    assert create_user_pos >= 0, "Create user test function not found"
    assert create_wallet_pos >= 0, "Create wallet test function not found"
    assert view_wallet_pos >= 0, "View wallet test function not found"
    assert create_user_pos < create_wallet_pos < view_wallet_pos, "Tests not in correct order"

    # Verify dependencies
    assert '@pytest.mark.dependency(depends=["test_test_create_user"])' in content
    assert '@pytest.mark.dependency(depends=["test_test_create_user", "test_test_create_wallet"])' in content

    # Verify fixtures
    assert "@pytest.fixture(scope='function')" in content
    assert "def USER_ID():" in content
    assert "def WALLET_ID():" in content

    # Verify variable storage
    assert "_variable_store['USER_ID'] = response" in content
    assert "_variable_store['WALLET_ID'] = response" in content


def test_circular_dependency_handling(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test handling of potential circular dependencies."""
    # Main request
    request = {
        "name": "Update User",
        "request": {
            "method": "PUT",
            "url": {"raw": "/users/{{USER_ID}}"}
        }
    }

    # Dependencies with circular reference
    dependencies = [
        {
            "endpoint": "Create User",
            "request": {
                "method": "POST",
                "url": {"raw": "/users"}
            },
            "sets": ["USER_ID"],
            "uses_variables": {"TEMP_ID": {"type": "dynamic"}}  # Circular reference
        },
        {
            "endpoint": "Create Temp",
            "request": {
                "method": "POST",
                "url": {"raw": "/temp/{{USER_ID}}"}  # Circular reference
            },
            "sets": ["TEMP_ID"]
        }
    ]

    # Map variables to their setting endpoints
    variables = {
        "USER_ID": ["Create User"],
        "TEMP_ID": ["Create Temp"]
    }

    content = content_generator.generate_test_content(
        request, dependencies, variables, fixture_generator
    )

    # Debug output
    print("\n=== Generated Content ===")
    print(content)
    print("\n=== Looking for test functions ===")
    print(f"Looking for: def test_test_create_user")
    print(f"Looking for: def test_test_create_temp")

    # Verify that circular dependencies are resolved by order of appearance
    create_user_pos = content.find("def test_test_create_user")
    create_temp_pos = content.find("def test_test_create_temp")

    print(f"Found positions - create_user: {create_user_pos}, create_temp: {create_temp_pos}")

    # Verify order
    assert create_user_pos >= 0, "Create user test function not found"
    assert create_temp_pos >= 0, "Create temp test function not found"
    assert create_user_pos < create_temp_pos, "Tests not in correct order"

    # Verify that variables are properly initialized
    assert "_variable_store['USER_ID'] = None" in content
    assert "_variable_store['TEMP_ID'] = None" in content


def test_error_handling_in_dependency_chain(
    content_generator: ContentGenerator, fixture_generator: FixtureGenerator
):
    """Test error handling in dependency chain."""
    # Main request
    request = {
        "name": "View Resource",
        "request": {
            "method": "GET",
            "url": {"raw": "/resources/{{RESOURCE_ID}}"}
        }
    }

    # Dependencies with potential errors
    dependencies = [
        {
            "endpoint": "Create Resource",
            "request": {
                "method": "POST",
                "url": {"raw": "/resources"}
            },
            "sets": ["RESOURCE_ID"]
        }
    ]

    variables = {"RESOURCE_ID": ["Create Resource"]}

    content = content_generator.generate_test_content(
        request, dependencies, variables, fixture_generator
    )

    # Verify error handling in variable storage
    assert "try:" in content
    assert "response_data = response.json()" in content
    assert "except ValueError as e:" in content
    assert "raise ValueError(f'Could not find ID in response" in content

    # Verify dependency error handling
    assert "pytest.skip" in content
    assert "pytest.fail" in content
