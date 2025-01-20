"""
Tests for authentication configuration generation.
"""

import pytest
from typing import Dict, Any
from src.generator.test import ContentGenerator, TestFileGenerator
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


def test_generate_auth_config(content_generator: ContentGenerator, tmp_path):
    """Test generating auth configuration."""
    # Create output directory
    output_dir = tmp_path / "generated_tests"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate test file to trigger conftest.py creation
    request_details = {
        "name": "Test request",
        "request": {"method": "GET", "url": {"raw": "https://api.test.com/test"}},
    }
    test_generator = TestFileGenerator(
        output_dir=str(output_dir),
        fixture_generator=FixtureGenerator(),
        auth_manager=content_generator.auth_manager,
    )
    test_generator.generate_test_file(request_details, [], {})

    # Read conftest.py to verify OAuth configuration
    conftest_path = output_dir / "conftest.py"
    conftest_content = conftest_path.read_text()

    # Verify OAuth configuration in conftest.py
    assert 'AUTH_TOKEN_URL = "https://auth.example.com/token"' in conftest_content
    assert 'BASIC_AUTH_USERNAME = "test_client"' in conftest_content
    assert 'BASIC_AUTH_PASSWORD = "test_secret"' in conftest_content
    assert 'if not all([BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, AUTH_TOKEN_URL]):' in conftest_content
    assert '    pytest.skip("Missing required environment variables for authentication")' in conftest_content


def test_generate_auth_fixture(content_generator: ContentGenerator):
    """Test generating auth fixture."""
    fixture_lines = "\n".join(content_generator._generate_auth_fixture())

    # Check fixture definition
    assert "@pytest.fixture(scope='session')" in fixture_lines
    assert "def auth_session(tls_verify):" in fixture_lines

    # Check OAuth2 setup
    assert "client = BackendApplicationClient(client_id=BASIC_AUTH_USERNAME)" in fixture_lines
    assert "session = OAuth2Session(client=client)" in fixture_lines

    # Check token fetching with error handling
    assert "try:" in fixture_lines
    assert "token = session.fetch_token(" in fixture_lines
    assert "verify=tls_verify" in fixture_lines
    assert "except Exception as e:" in fixture_lines
    assert 'pytest.skip(f"Failed to fetch OAuth token: {str(e)}")' in fixture_lines
    assert "return session" in fixture_lines
