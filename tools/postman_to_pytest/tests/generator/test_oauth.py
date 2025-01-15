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
def test_generator(auth_manager, tmp_path):
    """Create TestFileGenerator with auth manager."""
    output_dir = tmp_path / "generated_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    return TestFileGenerator(
        output_dir=str(output_dir),
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

        # Verify the generated test content has the correct OAuth header setup
        assert 'headers = {"Authorization": "Bearer {auth_session.token[\'access_token\']}"' in test_content
        
        # Run the test with required fixtures
        test_func = getattr(test_view_a_user, "test_test_get_view_a_user")
        test_func(session_instance, "https://api.test.com", True)

        # Verify API request basics
        assert session_instance.request.called
        request_args = session_instance.request.call_args
        assert request_args.kwargs["method"] == "GET"
        assert request_args.kwargs["url"] == "https://api.test.com/users/123"


def test_oauth_config_injection(test_generator, tmp_path):
    """Test OAuth configuration is properly injected into test files."""
    request_details = {
        "name": "Test request",
        "request": {"method": "GET", "url": {"raw": "https://api.test.com/test"}},
    }

    # Generate test file
    test_content = test_generator.generate_test_file(
        request_details=request_details, dependencies=[], variables={}
    )

    # Verify auth_session fixture is included
    assert "@pytest.fixture(scope='session')" in test_content
    assert "def auth_session(tls_verify):" in test_content
    assert "verify=tls_verify" in test_content

    # Read conftest.py to verify OAuth configuration
    conftest_path = tmp_path / "generated_tests" / "conftest.py"
    conftest_content = conftest_path.read_text()

    # Verify OAuth configuration in conftest.py
    assert 'AUTH_TOKEN_URL = "https://api.test.com/oauth/token"' in conftest_content
    assert 'BASIC_AUTH_USERNAME = "test_client"' in conftest_content
    assert 'BASIC_AUTH_PASSWORD = "test_secret"' in conftest_content


@responses.activate
def test_tls_verify_handling(test_generator, tmp_path):
    """Test TLS verification is properly handled."""
    request_details = {
        "name": "Test TLS",
        "request": {
            "method": "GET",
            "url": {"raw": "https://api.test.com/test"},
        },
    }

    # Test with TLS_VERIFY=false
    with patch.dict("os.environ", {"TLS_VERIFY": "false"}):
        test_content = test_generator.generate_test_file(
            request_details=request_details, dependencies=[], variables={}
        )
        test_file = tmp_path / "test_test_tls.py"
        test_file.write_text(test_content)

        # Import and run the generated test
        import sys

        sys.path.append(str(tmp_path))
        import test_test_tls

        # Verify tls_verify fixture is used in fetch_token and request
        assert "verify=tls_verify" in test_content

        # Import and verify the test file can be loaded without errors
        import sys

        sys.path.append(str(tmp_path))
        import test_test_tls
