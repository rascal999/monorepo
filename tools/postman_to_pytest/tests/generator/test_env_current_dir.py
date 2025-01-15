"""
Tests for environment file handling from current directory.
"""

import pytest
from pathlib import Path
from src.generator.fixtures import FixtureGenerator
from src.generator.test_file import TestFileGenerator


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

    # Mock Path to ensure consistent behavior
    original_path = Path
    class MockPath(type(Path())):
        _mock_files = {}
        _mock_exists = {}
        _mock_parents = {}

        @classmethod
        def reset(cls):
            cls._mock_files.clear()
            cls._mock_exists.clear()
            cls._mock_parents.clear()

        def __new__(cls, *args, **kwargs):
            path = original_path(*args, **kwargs)
            path_str = str(path)

            # Set up mock filesystem structure
            if path_str == str(output_dir):
                cls._mock_parents[path_str] = str(project_root)
                cls._mock_exists[path_str] = True
            elif path_str == str(current_dir):
                cls._mock_exists[path_str] = True
            elif path_str == str(current_dir / '.env'):
                cls._mock_exists[path_str] = True
                cls._mock_files[path_str] = current_env_content

            return path

        @property
        def parent(self):
            path_str = str(self)
            if path_str in self._mock_parents:
                return Path(self._mock_parents[path_str])
            # For paths not explicitly mocked, prevent accessing real filesystem
            if path_str.startswith(str(tmp_path)):
                parent_path = original_path(path_str).parent
                return Path(str(parent_path))
            return Path(str(current_dir))  # Default to current dir for unmocked paths

        def exists(self):
            path_str = str(self)
            return self._mock_exists.get(path_str, False)

        def read_text(self):
            path_str = str(self)
            if path_str in self._mock_files:
                return self._mock_files[path_str]
            raise FileNotFoundError(f"Mock file not found: {path_str}")

        def write_text(self, content):
            path_str = str(self)
            self._mock_files[path_str] = content
            self._mock_exists[path_str] = True
        
    # Reset mock state and set up Path mock
    MockPath.reset()
    monkeypatch.setattr("pathlib.Path", MockPath)

    # Initialize generator with current directory as base_dir
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(
        str(output_dir), fixture_gen, base_dir=str(current_dir)
    )

    # Verify .env was copied from current directory
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == current_env_content
