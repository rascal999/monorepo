"""
Tests for environment file handling when no env files exist.
"""

import pytest
from pathlib import Path
from src.generator.fixtures import FixtureGenerator
from src.generator.test_file import TestFileGenerator


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

    # Mock os.getcwd to return our test directory
    monkeypatch.setattr("os.getcwd", lambda: str(current_dir))

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
            elif path_str == str(project_root):
                cls._mock_exists[path_str] = True
            elif path_str == str(current_dir):
                cls._mock_exists[path_str] = True
            elif path_str == str(project_root.parent):
                cls._mock_exists[path_str] = True

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

    # Verify no .env file was created
    output_env = output_dir / ".env"
    assert not output_env.exists()
