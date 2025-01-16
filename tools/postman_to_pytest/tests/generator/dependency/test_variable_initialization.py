"""
Tests for variable initialization functionality.
"""

import pytest
from pathlib import Path
from src.generator.handlers.fixtures import FixtureGenerator
from src.generator.test import TestFileGenerator


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


def test_variable_initialization(test_generator: TestFileGenerator):
    """Test initialization of variable lists for request and dependencies."""
    request = {
        "name": "Get User",
        "request": {"method": "GET", "url": {"raw": "/users/{{user_id}}"}},
        "uses_variables": {
            "user_id": {"type": "dynamic"},
            "api_key": {"type": "environment"},
        },
        "uses": [],  # Initialize empty uses list
    }

    dependencies = [
        {
            "endpoint": "Create User",
            "request": {"method": "POST", "url": {"raw": "/users"}},
            "sets": ["user_id"],
            "uses_variables": {
                "token": {"type": "dynamic"},
                "env_var": {"type": "environment"},
            },
            "uses": [],  # Initialize empty uses list
        }
    ]

    variables = {"user_id": ["Create User"], "token": ["Login"]}

    # Generate test file
    content = test_generator.generate_test_file(request, dependencies, variables)

    # Verify request uses list contains only dynamic variables
    assert ("user_id", "dynamic") in request["uses"]
    assert not any("api_key" in use for use in request["uses"])

    # Verify dependency uses list contains only dynamic variables
    assert ("token", "dynamic") in dependencies[0]["uses"]
    assert not any("env_var" in use for use in dependencies[0]["uses"])
