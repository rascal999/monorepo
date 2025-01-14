"""
Tests for pytest fixture generation.
"""

import pytest
from pathlib import Path
from src.generator.fixtures import FixtureGenerator


def test_add_fixture():
    """Test adding fixtures."""
    generator = FixtureGenerator()

    # Add static fixture
    generator.add_fixture(
        name="api_key",
        var_type="static",
        scope="session",
        docstring="API key for authentication",
    )

    # Add dynamic fixture with dependencies
    generator.add_fixture(
        name="user_id",
        var_type="dynamic",
        dependencies=["auth_token"],
        docstring="User ID from create user response",
    )

    # Verify fixtures were added
    assert "api_key" in generator.fixtures
    assert "user_id" in generator.fixtures

    # Verify fixture details
    api_key = generator.fixtures["api_key"]
    assert api_key["type"] == "static"
    assert api_key["scope"] == "session"
    assert api_key["docstring"] == "API key for authentication"

    user_id = generator.fixtures["user_id"]
    assert user_id["type"] == "dynamic"
    assert user_id["dependencies"] == ["auth_token"]
    assert user_id["docstring"] == "User ID from create user response"


def test_generate_fixture_file(temp_dir: Path):
    """Test generating conftest.py file."""
    generator = FixtureGenerator()

    # Add fixtures
    generator.add_fixture(
        name="auth_token",
        var_type="dynamic",
        scope="function",
        docstring="Authentication token from login",
    )
    generator.add_fixture(
        name="user_id",
        var_type="dynamic",
        dependencies=["auth_token"],
        docstring="User ID from create user response",
    )

    # Generate conftest.py
    content = generator.generate_fixture_file(temp_dir)

    # Verify file was created
    conftest_path = temp_dir / "conftest.py"
    assert conftest_path.exists()

    # Verify content
    assert "import pytest" in content
    assert "_variable_store: Dict[str, Any] = {}" in content
    assert "@pytest.fixture" in content
    assert "def auth_token():" in content
    assert "def user_id(auth_token):" in content

    # Verify dynamic variable cleanup
    assert "yield value" in content
    assert "del _variable_store[" in content


def test_get_fixture_setup():
    """Test getting fixture setup code."""
    generator = FixtureGenerator()

    # Add fixtures
    generator.add_fixture(name="auth_token", var_type="dynamic")
    generator.add_fixture(name="api_key", var_type="static")

    # Test setup code for string value
    setup = generator.get_fixture_setup("auth_token", "Bearer abc123")
    assert setup == "_variable_store['auth_token'] = 'Bearer abc123'"

    # Test setup code for dict value
    value = {"id": 123, "name": "Test"}
    setup = generator.get_fixture_setup("api_key", value)
    assert setup == "_variable_store['api_key'] = {'id': 123, 'name': 'Test'}"

    # Test invalid fixture
    with pytest.raises(ValueError):
        generator.get_fixture_setup("invalid", "value")


def test_fixture_scoping(temp_dir: Path):
    """Test different fixture scopes."""
    generator = FixtureGenerator()

    # Add fixtures with different scopes
    generator.add_fixture(name="session_var", var_type="static", scope="session")
    generator.add_fixture(name="module_var", var_type="dynamic", scope="module")
    generator.add_fixture(name="function_var", var_type="dynamic", scope="function")

    # Generate conftest.py
    content = generator.generate_fixture_file(temp_dir)

    # Verify scope decorators
    assert '@pytest.fixture(scope="session")' in content
    assert '@pytest.fixture(scope="module")' in content
    assert '@pytest.fixture(scope="function")' in content


def test_fixture_dependencies(temp_dir: Path):
    """Test fixture dependency handling."""
    generator = FixtureGenerator()

    # Add fixtures with dependencies
    generator.add_fixture(name="auth_token", var_type="dynamic")
    generator.add_fixture(
        name="user_id", var_type="dynamic", dependencies=["auth_token"]
    )
    generator.add_fixture(
        name="user_details", var_type="dynamic", dependencies=["auth_token", "user_id"]
    )

    # Generate conftest.py
    content = generator.generate_fixture_file(temp_dir)

    # Verify dependency injection
    assert "def auth_token():" in content
    assert "def user_id(auth_token):" in content
    assert "def user_details(auth_token, user_id):" in content
