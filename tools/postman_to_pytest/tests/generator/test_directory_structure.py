"""
Tests for test file directory structure generation.
"""

import pytest
from pathlib import Path
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
