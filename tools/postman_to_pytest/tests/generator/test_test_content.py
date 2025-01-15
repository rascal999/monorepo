"""
Tests for test content generation functionality.
"""

import pytest
from typing import Dict, Any
from src.generator.test_content import TestContentGenerator
from src.generator.fixtures import FixtureGenerator
from src.generator.test_file import TestFileGenerator
from src.utils.auth import AuthManager


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
def auth_manager() -> AuthManager:
    """Create auth manager for testing."""
    import os
    os.environ["TESTING"] = "true"
    os.environ["OAUTH_TOKEN_URL"] = "https://auth.example.com/token"
    os.environ["BASIC_AUTH_USERNAME"] = "test_client"
    os.environ["BASIC_AUTH_PASSWORD"] = "test_secret"
    return AuthManager()


@pytest.fixture
def content_generator(auth_manager: AuthManager) -> TestContentGenerator:
    """Create test content generator."""
    return TestContentGenerator(auth_manager)


def test_generate_auth_config(content_generator: TestContentGenerator, tmp_path):
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
        auth_manager=content_generator.auth_manager
    )
    test_generator.generate_test_file(request_details, [], {})
    
    # Read conftest.py to verify OAuth configuration
    conftest_path = output_dir / "conftest.py"
    conftest_content = conftest_path.read_text()
    
    # Verify OAuth configuration in conftest.py
    assert 'AUTH_TOKEN_URL = "https://auth.example.com/token"' in conftest_content
    assert 'BASIC_AUTH_USERNAME = "test_client"' in conftest_content
    assert 'BASIC_AUTH_PASSWORD = "test_secret"' in conftest_content


def test_generate_imports(content_generator: TestContentGenerator):
    """Test generating import statements."""
    import_lines = "\n".join(content_generator._generate_imports())
    
    # Check essential imports
    assert "import pytest" in import_lines
    assert "import requests" in import_lines
    assert "import base64" in import_lines
    assert "import os" in import_lines
    assert "from typing import Dict, Any" in import_lines
    
    # Check environment variable imports
    assert "ENV_URL = os.getenv('ENV_URL')" in import_lines
    assert "CLIENT_ID = os.getenv('CLIENT_ID')" in import_lines
    assert "USER_LEGAL_OWNER = os.getenv('USER_LEGAL_OWNER')" in import_lines

def test_generate_test_with_env_variables(content_generator: TestContentGenerator, fixture_generator: FixtureGenerator):
    """Test generating test content with environment variables."""
    request_details = {
        "name": "View User",
        "request": {
            "method": "GET",
            "url": {"raw": "/v2.01/{{CLIENT_ID}}/users/{{USER_LEGAL_OWNER}}"},
        },
    }

    content = content_generator.generate_test_content(
        request_details,
        [],  # no dependencies
        {},  # no variables
        fixture_generator
    )

    # Verify environment variable imports
    assert "ENV_URL = os.getenv('ENV_URL')" in content
    assert "CLIENT_ID = os.getenv('CLIENT_ID')" in content
    assert "USER_LEGAL_OWNER = os.getenv('USER_LEGAL_OWNER')" in content

    # Verify URL formatting using environment variables
    assert 'url = f"{env_url}/v2.01/{CLIENT_ID}/users/{USER_LEGAL_OWNER}"' in content


def test_generate_auth_fixture(content_generator: TestContentGenerator):
    """Test generating auth fixture."""
    fixture_lines = "\n".join(content_generator._generate_auth_fixture())
    
    # Check fixture definition
    assert "@pytest.fixture(scope='session')" in fixture_lines
    assert "def auth_session(tls_verify):" in fixture_lines
    
    # Check OAuth2 setup
    assert "from requests_oauthlib import OAuth2Session" in fixture_lines
    assert "from oauthlib.oauth2 import BackendApplicationClient" in fixture_lines
    
    # Check environment variable imports
    assert "BASIC_AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME')" in fixture_lines
    assert "BASIC_AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD')" in fixture_lines
    assert "AUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')" in fixture_lines
    
    # Check token fetching
    assert "token = session.fetch_token(" in fixture_lines
    assert "verify=tls_verify" in fixture_lines
    assert "return session" in fixture_lines


def test_generate_test_function(content_generator: TestContentGenerator, fixture_generator: FixtureGenerator):
    """Test generating a test function."""
    # Add the user_data fixture first
    fixture_generator.add_fixture(
        name="user_data",
        var_type="dynamic",
        scope="function",
        docstring="User data from response"
    )
    
    request_details = {
        "method": "GET",
        "url": {"raw": "/users/{{user_id}}"},
        "sets": ["user_data"]
    }

    function_lines = content_generator._generate_test_function(
        name="test_get_user",
        request_details=request_details,
        dependencies=["test_create_user"],
        variables=["user_id"],
        fixture_generator=fixture_generator
    )
    
    # Check function definition
    assert '@pytest.mark.dependency(depends=["test_create_user"])' in function_lines
    assert "def test_get_user(auth_session, env_url, tls_verify, user_id):" in function_lines
    
    # Check request setup
    assert '    method = "GET"' in function_lines
    assert '    url = f"{env_url}/users/{{user_id}}"' in function_lines
    
    # Debug output
    print("\nGenerated function lines:")
    for line in function_lines:
        print(f"'{line}'")
    
    # Check response handling
    assert any(line.strip().startswith("response = auth_session.request(") for line in function_lines)
    assert any(line.strip() == "assert response.status_code == 200" for line in function_lines)


def test_generate_test_content(
    content_generator: TestContentGenerator,
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
        request,
        dependencies,
        variables,
        fixture_generator
    )

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


def test_dependency_ordering(content_generator: TestContentGenerator, fixture_generator: FixtureGenerator):
    """Test proper ordering of dependent tests."""
    # Main request
    request = {
        "name": "Get User Details",
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{user_id}}"},
        },
    }

    # Dependencies in specific order
    dependencies = [
        {
            "endpoint": "POST /auth/login",
            "request": {
                "method": "POST",
                "url": {"raw": "/auth/login"},
            },
            "sets": ["token"],
        },
        {
            "endpoint": "POST /users",
            "request": {
                "method": "POST",
                "url": {"raw": "/users"},
            },
            "sets": ["user_id"],
        },
    ]

    content = content_generator.generate_test_content(
        request,
        dependencies,
        {},
        fixture_generator
    )

    # Find positions of test functions
    login_pos = content.find("def test_test_post_auth_login")
    create_pos = content.find("def test_test_post_users")
    get_pos = content.find("def test_test_get_user_details")

    # Verify order
    assert login_pos < create_pos < get_pos
