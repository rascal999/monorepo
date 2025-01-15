"""
Tests for test file generation functionality.
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


def test_env_file_copying_project_root(tmp_path: Path, monkeypatch):
    """Test copying .env file from project root directory."""
    # Create fake project root with .env
    project_root = tmp_path / "project_root"
    project_root.mkdir()
    root_env_content = "ROOT_VAR=root_value"
    (project_root / ".env").write_text(root_env_content)
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock project root path
    def mock_project_root(self):
        return project_root
    monkeypatch.setattr(Path, "parent", property(lambda self: mock_project_root(self)))
    
    # Initialize generator
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen)
    
    # Verify .env was copied from project root
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == root_env_content


def test_env_file_copying_current_dir(tmp_path: Path, monkeypatch):
    """Test copying .env file from current directory when not in project root."""
    # Create fake project root without .env
    project_root = tmp_path / "project_root"
    project_root.mkdir()
    
    # Create current directory with .env
    current_dir = tmp_path / "current_dir"
    current_dir.mkdir()
    current_env_content = "CURRENT_VAR=current_value"
    (current_dir / ".env").write_text(current_env_content)
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock project root path
    def mock_project_root(self):
        return project_root
    monkeypatch.setattr(Path, "parent", property(lambda self: mock_project_root(self)))
    
    # Initialize generator with current directory as base_dir
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen, base_dir=str(current_dir))
    
    # Verify .env was copied from current directory
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == current_env_content


def test_env_file_copying_with_sample(tmp_path: Path, monkeypatch):
    """Test copying .env.sample when no .env exists in either location."""
    # Create fake project root with .env.sample
    project_root = tmp_path / "project_root"
    project_root.mkdir()
    sample_content = "SAMPLE_VAR=sample_value"
    (project_root / ".env.sample").write_text(sample_content)
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock project root path
    def mock_project_root(self):
        return project_root
    monkeypatch.setattr(Path, "parent", property(lambda self: mock_project_root(self)))
    
    # Initialize generator
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen)
    
    # Verify .env.sample was copied as .env
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == sample_content


def test_output_directory_creation(tmp_path: Path, monkeypatch):
    """Test output directory is created if it doesn't exist."""
    # Create fake project root with .env
    project_root = tmp_path / "project_root"
    project_root.mkdir()
    env_content = "TEST_VAR=test_value"
    (project_root / ".env").write_text(env_content)
    
    # Define output directory but don't create it
    output_dir = tmp_path / "output"
    assert not output_dir.exists()
    
    # Mock project root path
    def mock_project_root(self):
        return project_root
    monkeypatch.setattr(Path, "parent", property(lambda self: mock_project_root(self)))
    
    # Initialize generator - should create output directory
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen)
    
    # Verify output directory was created and .env was copied
    assert output_dir.exists()
    assert (output_dir / ".env").exists()
    assert (output_dir / ".env").read_text() == env_content


def test_conftest_generation(tmp_path: Path, monkeypatch):
    """Test generation of conftest.py with environment variables and auth fixture."""
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create mock auth manager
    class MockAuthManager:
        oauth_token_url = "https://api.example.com/oauth/token"
        basic_auth_username = "test_user"
        basic_auth_password = "test_pass"
    
    # Initialize generator with mock auth manager
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen, auth_manager=MockAuthManager())
    
    # Verify conftest.py was created
    conftest_path = output_dir / "conftest.py"
    assert conftest_path.exists()
    
    # Verify content
    content = conftest_path.read_text()
    assert "import os" in content
    assert "import base64" in content
    assert "import pytest" in content
    assert "from dotenv import load_dotenv" in content
    assert "ENV_URL = os.getenv('ENV_URL')" in content
    assert "TLS_VERIFY = os.getenv('TLS_VERIFY', 'true').lower() == 'true'" in content
    assert 'AUTH_TOKEN_URL = "https://api.example.com/oauth/token"' in content
    assert 'BASIC_AUTH_USERNAME = "test_user"' in content
    assert 'BASIC_AUTH_PASSWORD = "test_pass"' in content
    assert "@pytest.fixture(scope='session')" in content
    assert "def auth_session():" in content


def test_conftest_generation_no_auth(tmp_path: Path, monkeypatch):
    """Test generation of conftest.py without auth manager."""
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Initialize generator without auth manager
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen)
    
    # Verify conftest.py was created
    conftest_path = output_dir / "conftest.py"
    assert conftest_path.exists()
    
    # Verify content
    content = conftest_path.read_text()
    assert "AUTH_TOKEN_URL = None" in content
    assert "BASIC_AUTH_USERNAME = None" in content
    assert "BASIC_AUTH_PASSWORD = None" in content


def test_env_file_copying_no_files(tmp_path: Path, monkeypatch):
    """Test behavior when no .env or .env.sample exists in any location."""
    # Create fake project root without any env files
    project_root = tmp_path / "project_root"
    project_root.mkdir()
    
    # Create current directory without any env files
    current_dir = tmp_path / "current_dir"
    current_dir.mkdir()
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock project root path
    def mock_project_root(self):
        return project_root
    monkeypatch.setattr(Path, "parent", property(lambda self: mock_project_root(self)))
    
    # Initialize generator with current directory as base_dir
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen, base_dir=str(current_dir))
    
    # Verify no .env file was created
    output_env = output_dir / ".env"
    assert not output_env.exists()


def test_variable_initialization(test_generator: TestFileGenerator):
    """Test initialization of variable lists for request and dependencies."""
    request = {
        "name": "Get User",
        "request": {
            "method": "GET",
            "url": {"raw": "/users/{{user_id}}"}
        },
        "uses_variables": {
            "user_id": {"type": "dynamic"},
            "api_key": {"type": "environment"}
        },
        "uses": []  # Initialize empty uses list
    }
    
    dependencies = [{
        "endpoint": "Create User",
        "request": {
            "method": "POST",
            "url": {"raw": "/users"}
        },
        "sets": ["user_id"],
        "uses_variables": {
            "token": {"type": "dynamic"},
            "env_var": {"type": "environment"}
        },
        "uses": []  # Initialize empty uses list
    }]

    variables = {"user_id": ["Create User"], "token": ["Login"]}
    
    # Generate test file
    content = test_generator.generate_test_file(request, dependencies, variables)
    
    # Verify request uses list contains only dynamic variables
    assert ("user_id", "dynamic") in request["uses"]
    assert not any("api_key" in use for use in request["uses"])
    
    # Verify dependency uses list contains only dynamic variables
    assert ("token", "dynamic") in dependencies[0]["uses"]
    assert not any("env_var" in use for use in dependencies[0]["uses"])
