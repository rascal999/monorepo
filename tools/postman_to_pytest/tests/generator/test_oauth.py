"""Tests for OAuth authentication in generated test files."""

import pytest
import responses
from unittest.mock import MagicMock, patch
from src.utils.auth import AuthManager
from src.generator.test_file import TestFileGenerator
from src.generator.fixtures import FixtureGenerator


@pytest.fixture
def auth_manager():
    """Create AuthManager with test credentials."""
    with patch.dict(
        "os.environ",
        {
            "TESTING": "true",  # Enable test mode
            "BASIC_AUTH_USERNAME": "test_client",
            "BASIC_AUTH_PASSWORD": "test_secret",
            "OAUTH_TOKEN_URL": "https://api.test.com/oauth/token",
            "OAUTH_SCOPE": "read write",
            "AUTH_HEADER": "Authorization",
        },
    ):
        return AuthManager()


@pytest.fixture
def test_generator(auth_manager):
    """Create TestFileGenerator with auth manager."""
    return TestFileGenerator(
        output_dir="generated_tests",
        fixture_generator=FixtureGenerator(),
        auth_manager=auth_manager,
    )


@responses.activate
def test_oauth_authentication_flow(test_generator, tmp_path):
    """Test OAuth authentication flow in generated test files."""
    # Create test request details
    request_details = {
        "name": "View a user",
        "request": {
            "method": "GET",
            "url": {"raw": "https://api.test.com/users/123", "path": ["users", "123"]},
            "header": [],
        },
    }

    # Generate test file
    test_content = test_generator.generate_test_file(
        request_details=request_details, dependencies=[], variables={}
    )

    # Write test file
    test_file = tmp_path / "test_view_a_user.py"
    test_file.write_text(test_content)

    # Import and run the generated test
    import sys

    sys.path.append(str(tmp_path))
    import test_view_a_user

    # Run the test function
    with patch("requests_oauthlib.OAuth2Session") as mock_oauth:
        # Configure mock session
        session_instance = mock_oauth.return_value
        session_instance.token = {"access_token": "test_token"}
        session_instance.request.return_value.status_code = 200

        # Run the test
        test_func = getattr(test_view_a_user, "test_test_view_a_user")
        test_func(session_instance)

        # Verify API request
        assert session_instance.request.called
        request_args = session_instance.request.call_args
        assert request_args.kwargs["method"] == "GET"
        assert request_args.kwargs["url"] == "https://api.test.com/users/123"
        assert request_args.kwargs["headers"]["Authorization"] == "Bearer test_token"


def test_oauth_config_injection(test_generator):
    """Test OAuth configuration is properly injected into test files."""
    request_details = {
        "name": "Test request",
        "request": {"method": "GET", "url": {"raw": "https://api.test.com/test"}},
    }

    # Generate test file
    test_content = test_generator.generate_test_file(
        request_details=request_details, dependencies=[], variables={}
    )

    # Verify OAuth configuration is present
    assert 'AUTH_TOKEN_URL = "https://api.test.com/oauth/token"' in test_content
    assert 'BASIC_AUTH_USERNAME = "test_client"' in test_content
    assert 'BASIC_AUTH_PASSWORD = "test_secret"' in test_content

    # Verify auth_session fixture is included
    assert "@pytest.fixture(scope='session')" in test_content
    assert "def auth_session():" in test_content
    assert "Basic {auth_header}" in test_content
