"""
Path handling utilities.
"""

import os
import re
from pathlib import Path
from typing import List


def sanitize_path(path: str) -> str:
    """Convert path to safe format for file system.

    Args:
        path: Original path string

    Returns:
        Sanitized path safe for file system
    """
    if not path:
        return ""

    # Replace path separators with underscore
    sanitized = re.sub(r"[/\\]", "_", path)

    # Replace each invalid character with underscore
    invalid_chars = '<>:"|?*'
    for c in invalid_chars:
        sanitized = sanitized.replace(c, "_")

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")

    # Preserve existing multiple underscores
    return sanitized


def ensure_directory(path: str) -> None:
    """Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Raises:
        OSError: If directory creation fails or if path is empty
    """
    if not path:
        raise OSError("Empty path provided")

    if os.path.isfile(path):
        raise OSError(f"Path exists and is a file: {path}")

    Path(path).mkdir(parents=True, exist_ok=True)


def get_relative_path(base_path: str, full_path: str) -> List[str]:
    """Get relative path components from base to full path.

    Args:
        base_path: Base directory path
        full_path: Full path to get relative components for

    Returns:
        List of path components relative to base
    """
    # Convert to Path objects and normalize separators
    base = Path(base_path).resolve()
    full = Path(full_path).resolve()

    # Handle same path case
    if base == full:
        return []

    try:
        # Get relative path and normalize separators
        relative = full.relative_to(base)
        # Convert to list of parts, filtering out '.' and empty parts
        parts = [part for part in relative.parts if part and part != "."]
        # Handle Windows paths by using pathlib to normalize
        return [str(Path(part).name) for part in parts]
    except ValueError:
        # Path is not relative to base, return just filename
        return [full.name]


def join_paths(*paths: str) -> str:
    """Join path components in a cross-platform way.

    Args:
        *paths: Path components to join

    Returns:
        Joined path string

    Raises:
        TypeError: If no paths provided
    """
    if not paths:
        raise TypeError("No path components provided")

    # Handle single path case
    if len(paths) == 1:
        return paths[0]

    # Join paths using pathlib for cross-platform compatibility
    result = Path(paths[0])
    for path in paths[1:]:
        # Skip empty path components
        if path:
            result = result / path

    return str(result)
