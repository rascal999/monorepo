"""
Tests for output directory and conftest.py generation functionality.
"""

import os
import pytest
from pathlib import Path
from src.generator.fixtures import FixtureGenerator
from src.generator.test_file import TestFileGenerator


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

    # Mock Path to ensure consistent behavior
    original_path = Path
    class MockPath(type(Path())):
        _mock_files = {}

        def __new__(cls, *args, **kwargs):
            path = original_path(*args, **kwargs)
            path_str = str(path)
            # Handle all possible paths
            if path_str == str(output_dir):
                # For output_dir itself
                path.__dict__['_parent'] = project_root
                path.__dict__['_exists'] = False
            elif path_str == str(project_root):
                # For project_root itself
                path.__dict__['_exists'] = True
            elif path_str == str(project_root / '.env'):
                # For .env in project root
                path.__dict__['_exists'] = True
                path.__dict__['_content'] = env_content
            elif path_str == str(project_root / '.env.sample'):
                # For .env.sample in project root
                path.__dict__['_exists'] = False
            elif path_str == str(Path(output_dir) / '.env'):
                # For output .env file
                path.__dict__['_exists'] = False
            elif path_str == str(Path(os.getcwd()) / '.env'):
                # For base directory .env file
                path.__dict__['_exists'] = False
            return path

        @property
        def parent(self):
            return self.__dict__.get('_parent', original_path(str(self)).parent)

        def exists(self):
            return self.__dict__.get('_exists', original_path(str(self)).exists())

        def read_text(self):
            if '_content' in self.__dict__:
                return self.__dict__['_content']
            path_str = str(self)
            if path_str in self._mock_files:
                return self._mock_files[path_str]
            return original_path(str(self)).read_text()

        def write_text(self, content):
            self._mock_files[str(self)] = content
        
        def mkdir(self, parents=False, exist_ok=False):
            self.__dict__['_exists'] = True
            if parents:
                parent = self.parent
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=exist_ok)

    monkeypatch.setattr("pathlib.Path", MockPath)

    # Initialize generator - should create output directory
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(
        output_dir=str(output_dir),
        fixture_generator=fixture_gen,
        base_dir=str(project_root)
    )

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
    generator = TestFileGenerator(
        str(output_dir), fixture_gen, auth_manager=MockAuthManager()
    )

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


def test_test_file_generation(tmp_path: Path):
    """Test generation of test files from request details."""
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Create mock request details
    request_details = {
        "name": "test_request",
        "request": {
            "method": "GET",
            "url": {
                "raw": "https://api.example.com/users"
            }
        }
    }

    # Initialize generator
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen)

    # Generate test file
    content = generator.generate_test_file(
        request_details=request_details,
        dependencies=[],
        variables={}
    )

    # Verify test file was created
    test_file = output_dir / "test_api.py"
    assert test_file.exists()
    assert test_file.read_text() == content

    # Verify content includes test function
    assert "def test_test_get_test_request" in content
    assert "method = \"GET\"" in content
    assert "assert response.status_code == 200" in content
