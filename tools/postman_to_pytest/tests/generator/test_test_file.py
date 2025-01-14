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
    return TestFileGenerator(str(tmp_path), fixture_generator)


def test_sanitize_name(test_generator: TestFileGenerator):
    """Test sanitizing names for Python identifiers."""
    # Test basic conversion
    assert test_generator._sanitize_name("Get User") == "test_get_user"

    # Test with special characters
    assert test_generator._sanitize_name("Create User (v2)") == "test_create_user_v2"

    # Test with leading number
    assert test_generator._sanitize_name("2FA Setup") == "test_2fa_setup"


def test_format_request_details(test_generator: TestFileGenerator):
    """Test formatting request details as Python code."""
    request = {
        "method": "POST",
        "url": {"raw": "http://api.example.com/users", "path": ["users"]},
        "header": [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Authorization", "value": "Bearer {{token}}"},
        ],
        "body": {"mode": "raw", "raw": '{"name": "test"}'},
    }

    lines = test_generator._format_request_details(request)

    # Verify method
    assert any('method = "POST"' in line for line in lines)

    # Verify URL formatting
    assert any('url = "http://api.example.com/users"' in line for line in lines)

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
            "url": {"raw": "http://api.example.com/users"},
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


def test_dependency_ordering(test_generator: TestFileGenerator):
    """Test proper ordering of dependent tests."""
    # Main request
    request = {
        "name": "Get User Details",
        "request": {
            "method": "GET",
            "url": {"raw": "http://api.example.com/users/{{user_id}}"},
        },
    }

    # Dependencies in specific order
    dependencies = [
        {
            "endpoint": "POST /auth/login",
            "request": {
                "method": "POST",
                "url": {"raw": "http://api.example.com/auth/login"},
            },
            "sets": ["token"],
        },
        {
            "endpoint": "POST /users",
            "request": {
                "method": "POST",
                "url": {"raw": "http://api.example.com/users"},
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
