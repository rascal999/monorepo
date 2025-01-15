"""
Tests for environment file handling from .env.sample.
"""

import pytest
from pathlib import Path
from src.generator.fixtures import FixtureGenerator
from src.generator.test_file import TestFileGenerator


def test_env_file_copying_with_sample(tmp_path: Path, monkeypatch):
    """Test copying .env.sample when no .env exists in either location."""
    # Create project structure
    project_parent = tmp_path / "project_parent"
    project_parent.mkdir()
    project_root = project_parent / "project_root"
    project_root.mkdir()

    # Create .env.sample in project parent (which will be the project root from TestFileGenerator's perspective)
    sample_content = "SAMPLE_VAR=sample_value"
    (project_parent / ".env.sample").write_text(sample_content)

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Mock os.getcwd to return our test directory
    monkeypatch.setattr("os.getcwd", lambda: str(project_root))

    # Mock os.makedirs to prevent real filesystem operations
    monkeypatch.setattr("os.makedirs", lambda p, exist_ok: None)

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
            print(f"\nMockPath.__new__ called for: {path_str}")
            print(f"Current mock state:")
            print(f"  _mock_files: {cls._mock_files}")
            print(f"  _mock_exists: {cls._mock_exists}")
            print(f"  _mock_parents: {cls._mock_parents}")

            # Set up mock filesystem structure
            if path_str == str(output_dir):
                print(f"Setting up output_dir: {path_str}")
                cls._mock_parents[path_str] = str(project_root)
                cls._mock_exists[path_str] = True
            elif path_str == str(project_root):
                print(f"Setting up project_root: {path_str}")
                cls._mock_exists[path_str] = True
                cls._mock_parents[path_str] = str(project_parent)
            elif path_str == str(project_parent):
                print(f"Setting up project_parent: {path_str}")
                cls._mock_exists[path_str] = True
            elif path_str == str(project_parent / '.env.sample'):
                print(f"Setting up .env.sample: {path_str}")
                cls._mock_exists[path_str] = True
                cls._mock_files[path_str] = sample_content
            elif path_str == str(output_dir / '.env'):
                print(f"Setting up output .env: {path_str}")
                # Don't set exists=True here, let write_text handle that
                if path_str in cls._mock_files:
                    cls._mock_exists[path_str] = True

            print(f"Updated mock state:")
            print(f"  _mock_files: {cls._mock_files}")
            print(f"  _mock_exists: {cls._mock_exists}")
            print(f"  _mock_parents: {cls._mock_parents}")
            return path

        @property
        def parent(self):
            path_str = str(self)
            print(f"\nMockPath.parent called for: {path_str}")
            if path_str in self._mock_parents:
                parent = Path(self._mock_parents[path_str])
                print(f"Found in _mock_parents: {parent}")
                return parent
            # For paths not explicitly mocked, prevent accessing real filesystem
            if path_str.startswith(str(tmp_path)):
                parent_path = original_path(path_str).parent
                print(f"Using tmp_path parent: {parent_path}")
                return Path(str(parent_path))
            if path_str == str(project_root):
                print(f"Using project_parent for project_root: {project_parent}")
                return Path(str(project_parent))
            print(f"Using default project_parent: {project_parent}")
            return Path(str(project_parent))

        def exists(self):
            path_str = str(self)
            exists = self._mock_exists.get(path_str, False)
            print(f"\nMockPath.exists called for: {path_str}")
            print(f"Result: {exists}")
            return exists

        def read_text(self):
            path_str = str(self)
            print(f"\nMockPath.read_text called for: {path_str}")
            if path_str in self._mock_files:
                content = self._mock_files[path_str]
                print(f"Found content: {content}")
                return content
            print(f"File not found in mock files")
            raise FileNotFoundError(f"Mock file not found: {path_str}")

        def write_text(self, content):
            path_str = str(self)
            print(f"\nMockPath.write_text called for: {path_str}")
            print(f"Content: {content}")
            self._mock_files[path_str] = content
            self._mock_exists[path_str] = True
            print(f"Updated mock state:")
            print(f"  _mock_files: {self._mock_files}")
            print(f"  _mock_exists: {self._mock_exists}")
        
    # Reset mock state and set up Path mock
    MockPath.reset()
    monkeypatch.setattr("pathlib.Path", MockPath)

    # Initialize generator
    fixture_gen = FixtureGenerator()
    generator = TestFileGenerator(str(output_dir), fixture_gen)

    # Verify .env.sample was copied as .env
    output_env = output_dir / ".env"
    assert output_env.exists()
    assert output_env.read_text() == sample_content
