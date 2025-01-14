"""
Tests for pytest test file generation.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from src.generator.fixtures import FixtureGenerator
from src.generator.test_file import TestFileGenerator


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
def test_generator(
    tmp_path: Path, fixture_generator: FixtureGenerator
) -> TestFileGenerator:
    """Create test file generator."""
    return TestFileGenerator(str(tmp_path), fixture_generator, base_dir=str(tmp_path))


def test_sanitize_name(test_generator: TestFileGenerator):
    """Test sanitizing names for Python identifiers."""
    # Test basic conversion
    assert test_generator._sanitize_name("Get User") == "test_get_user"

    # Test with special characters
    assert test_generator._sanitize_name("Create User (v2)") == "test_create_user_v2"

    # Test with leading number
    assert test_generator._sanitize_name("2FA Setup") == "test_2fa_setup"


@pytest.fixture(autouse=True)
def setup_env():
    """Setup test environment variables."""
    import os
    os.environ["ENV_URL"] = "http://api.example.com"
    yield
    del os.environ["ENV_URL"]

def test_format_request_details(test_generator: TestFileGenerator):
    """Test formatting request details as Python code."""
    request = {
        "method": "POST",
        "url": {"raw": "/users", "path": ["users"]},
        "header": [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Authorization", "value": "Bearer {{token}}"},
        ],
        "body": {"mode": "raw", "raw": '{"name": "test"}'},
    }

    lines = test_generator._format_request_details(request)

    # Verify method
    assert any('method = "POST"' in line for line in lines)

    # Verify URL formatting with ENV_URL
    assert any('url = f"{ENV_URL}/users"' in line for line in lines)

    # Verify headers formatting
    headers_line = next(line for line in lines if "headers =" in line)
    assert '"Content-Type": "application/json"' in headers_line
    assert '"Authorization": "Bearer {{token}}"' in headers_line

    # Verify body formatting
    body_line = next(line for line in lines if "data =" in line)
    assert '{"name": "test"}' in body_line


def test_generate_test_file(
    test_generator: TestFileGenerator,
    sample_collection: Dict[str, Any],
    sample_dependencies: Dict[str, Any],
):
    """Test generating complete test file."""
    # Get request details from sample collection
    request = {
        "name": "Get User",
        "path": ["Users"],
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

    # Generate test file
    content = test_generator.generate_test_file(request, dependencies, variables)

    # Verify imports
    assert "import pytest" in content
    assert "import requests" in content

    # Verify dependency test
    assert "@pytest.mark.dependency()" in content
    assert "def test_test_post_auth_login" in content

    # Verify main test
    assert "def test_test_get_user" in content
    assert "@pytest.mark.dependency(depends=[" in content

    # Verify request handling
    assert "response = auth_session.request(" in content
    assert "assert response.status_code == 200" in content


def test_directory_structure(test_generator: TestFileGenerator):
    """Test output directory structure creation."""
    request = {
        "name": "Create User",
        "path": ["Users", "Management"],
        "request": {
            "method": "POST",
            "url": {"raw": "/users"},
            "body": {"mode": "raw", "raw": "{}"},
        },
    }

    # Generate test file
    content = test_generator.generate_test_file(request, [], {})

    # Create expected directory structure
    test_dir = Path(test_generator.output_dir) / "Users" / "Management"
    test_dir.mkdir(parents=True, exist_ok=True)

    # Write test file
    test_path = test_dir / "test_create_user.py"
    test_path.write_text(content)

    # Verify directory structure and content
    assert test_path.exists()
    assert test_path.read_text() == content


def test_url_formatting_with_variables(test_generator: TestFileGenerator):
    """Test URL formatting with empty segments and variable placeholders."""
    # Test dictionary URL with empty segments and variables
    request_dict = {
        "method": "GET",
        "url": {
            "raw": "/v2.01//{{CLIENT_ID}}/users/{{USER_ID}}",
            "path": ["v2.01", "", "{{CLIENT_ID}}", "users", "{{USER_ID}}"]
        }
    }
    
    lines = test_generator._format_request_details(request_dict)
    url_line = next(line for line in lines if "url =" in line)
    assert 'url = f"{ENV_URL}/v2.01/{{CLIENT_ID}}/users/{{USER_ID}}"' in url_line

    # Test string URL with empty segments and variables
    request_str = {
        "method": "GET",
        "url": "/v2.01//{{CLIENT_ID}}//users/{{USER_ID}}"
    }
    
    lines = test_generator._format_request_details(request_str)
    url_line = next(line for line in lines if "url =" in line)
    assert 'url = f"{ENV_URL}/v2.01/{{CLIENT_ID}}/users/{{USER_ID}}"' in url_line


def test_env_file_copying_with_env(tmp_path: Path):
    """Test copying .env file to output directory when .env exists."""
    # Create test .env file
    env_content = "TEST_VAR=test_value"
    (tmp_path / ".env").write_text(env_content)
    
    # Create test .env.sample file (should be ignored when .env exists)
    (tmp_path / ".env.sample").write_text("TEST_VAR=sample_value")
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Initialize generator with test paths
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen, base_dir=str(tmp_path))
    
    # Verify .env was copied to output
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == env_content


def test_env_file_copying_with_sample(tmp_path: Path):
    """Test copying .env.sample as .env when no .env exists."""
    # Create test .env.sample file
    sample_content = "TEST_VAR=sample_value"
    (tmp_path / ".env.sample").write_text(sample_content)
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Initialize generator with test paths
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen, base_dir=str(tmp_path))
    
    # Verify .env.sample was copied as .env
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == sample_content


def test_env_file_copying_no_files(tmp_path: Path):
    """Test behavior when neither .env nor .env.sample exist."""
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Initialize generator with test paths
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen, base_dir=str(tmp_path))
    
    # Verify no .env file was created
    output_env = output_dir / ".env"
    assert not output_env.exists()


def test_dependency_ordering(test_generator: TestFileGenerator):
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

    content = test_generator.generate_test_file(request, dependencies, {})

    # Find positions of test functions
    login_pos = content.find("def test_test_post_auth_login")
    create_pos = content.find("def test_test_post_users")
    get_pos = content.find("def test_test_get_user_details")

    # Verify order
    assert login_pos < create_pos < get_pos
