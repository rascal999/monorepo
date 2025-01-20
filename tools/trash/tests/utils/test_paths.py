"""
Tests for path handling utilities.
"""

from pathlib import Path
from src.utils.paths import (
    sanitize_path,
    ensure_directory,
    get_relative_path,
    join_paths,
)


def test_sanitize_path():
    """Test path sanitization."""
    # Test basic sanitization
    assert sanitize_path("hello/world") == "hello_world"

    # Test invalid characters
    assert sanitize_path('test<>:"/\\|?*file') == "test_________file"

    # Test leading/trailing spaces and dots
    assert sanitize_path(" .test. ") == "test"

    # Test multiple underscores
    assert sanitize_path("test___file") == "test___file"

    # Test empty path
    assert sanitize_path("") == ""


def test_ensure_directory(tmp_path: Path):
    """Test directory creation."""
    # Test creating single directory
    test_dir = tmp_path / "test_dir"
    ensure_directory(str(test_dir))
    assert test_dir.exists()
    assert test_dir.is_dir()

    # Test creating nested directories
    nested_dir = tmp_path / "parent" / "child" / "grandchild"
    ensure_directory(str(nested_dir))
    assert nested_dir.exists()
    assert nested_dir.is_dir()

    # Test with existing directory
    ensure_directory(str(test_dir))  # Should not raise error


def test_get_relative_path(tmp_path: Path):
    """Test relative path extraction."""
    # Test basic relative path
    base = tmp_path / "base"
    full = base / "sub" / "file.txt"
    assert get_relative_path(str(base), str(full)) == ["sub", "file.txt"]

    # Test same path
    assert get_relative_path(str(base), str(base)) == []

    # Test non-relative path
    other = tmp_path / "other" / "file.txt"
    assert get_relative_path(str(base), str(other)) == ["file.txt"]


def test_join_paths():
    """Test path joining."""
    # Test basic joining
    assert join_paths("path", "to", "file") == str(Path("path/to/file"))

    # Test with empty components
    assert join_paths("path", "", "file") == str(Path("path/file"))

    # Test single path
    assert join_paths("path") == "path"


def test_path_edge_cases():
    """Test edge cases for path handling."""
    # Test empty path for sanitize
    assert sanitize_path("") == ""

    # Test empty path for ensure_directory
    try:
        ensure_directory("")
        assert False, "Should raise OSError"
    except OSError:
        pass

    # Test empty paths for join_paths
    try:
        join_paths()
        assert False, "Should raise TypeError"
    except TypeError:
        pass


def test_path_normalization():
    """Test path normalization behavior."""
    # Test sanitize_path with different separators
    assert sanitize_path("path\\to/file") == "path_to_file"

    # Test get_relative_path with different separators
    base = "path/to"
    full = "path/to/file"
    components = get_relative_path(base, full)
    assert components == ["file"]
